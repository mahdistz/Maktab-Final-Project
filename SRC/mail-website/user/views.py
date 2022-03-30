import random
import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from utils import send_otp_code
from .forms import UserRegisterForm, VerifyCodeForm, CreateContactForm, ContactUpdateForm, SearchContactForm
from django.contrib.auth import login, authenticate
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import Users, CodeRegister, Contact
from .serializers import ContactSerializer
from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordContextMixin
from django.views.generic import FormView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from .forms import PasswordResetForm
from django.conf import settings
from django.contrib.auth.views import LoginView
from .forms import LoginForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView
from user.models import Contact
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect, Http404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse


@csrf_exempt
@api_view(["GET"])
def sample_api(request):
    data = {'sample_data': 123}
    return Response(data, status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def api_contacts_of_user(request):
    user_id = request.user.id
    user = Users.objects.get(id=user_id)
    contacts = user.contacts.values('name', 'email', 'phone_number', 'other_email',
                                    'birth_date')
    data = {'contacts': contacts}
    return Response(data, status=HTTP_200_OK)


def index(request):
    return render(request, 'user/index.html', {'title': 'index'})


@login_required(login_url=settings.LOGIN_URL)
def home(request):
    return render(request, 'home.html', {})


# Class based view that extends from the built-in login view to add remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            # set session expiry to 0 seconds.
            # So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)
            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True
        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class SignUpView(View):
    form_class = UserRegisterForm
    # template_name = 'register/index.html'
    template_name = 'user/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/home/')
        # else process dispatch as it otherwise normally would
        return super(SignUpView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            if str(form.cleaned_data['verification']) == 'Email':

                # EMAIL
                current_site = get_current_site(request)
                subject = 'Activate Your Account'
                message = render_to_string('user/acc_active_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                user.email_user(subject, message)

                messages.success(request, 'Please Confirm your email to complete registration.')
                return redirect('login')
            elif str(form.cleaned_data['verification']) == 'Phone':

                # SMS
                code = random.randint(100000, 999999)
                CodeRegister.objects.create(phone_number=form.cleaned_data['phone'],
                                            code=code)
                # kavenegar service
                send_otp_code(form.cleaned_data['phone'], code)
                # Sending session to other url for verifying user with sms code.
                request.session['user_registering'] = {
                    'username': form.cleaned_data['username'],
                    'password1': form.cleaned_data['password1'],
                    'password2': form.cleaned_data['password2'],
                    'verification': form.cleaned_data['verification'],
                    'phone': form.cleaned_data['phone'],
                    'email': form.cleaned_data['email'],
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'nationality': form.cleaned_data['nationality'],
                    'birth_date': form.cleaned_data['birth_date'].isoformat(),
                    'gender': form.cleaned_data['gender'],
                }
                messages.success(request, 'we sent you a code', 'success')
                return redirect('verify')

        return render(request, self.template_name, {'form': form})


# Verify with phone number
class VerifyCodeView(View):
    form_class = VerifyCodeForm
    template_name = 'user/verify-register-phone.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_session = request.session['user_registering']
        code_instance = CodeRegister.objects.get(phone_number=user_session['phone'])
        user = Users.objects.get(phone=user_session['phone'])
        form = self.form_class(request.POST)
        if form.is_valid():
            if str(form.cleaned_data['code']) == str(code_instance):
                user.is_active = True
                user.username += "@mail.com"
                user.save()
                code_instance.delete()
                messages.success(request, 'you registered!')
                return redirect('login')
            else:
                messages.error(request, 'this code is wrong')
                return redirect('verify')
        else:
            return redirect('index')


# Activate account with email
class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.username += '@mail.com'
            user.save()
            login(request, user)
            messages.success(request, 'Your account have been confirmed.')
            return redirect('index')
        else:
            messages.warning(request, 'The confirmation link was invalid, possibly because it has already been used.')
            return redirect('register')


UserModel = get_user_model()


# reset password with phone number
class ResetPasswordPhoneView(PasswordContextMixin, FormView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'password/password_reset.html'
    token_generator = default_token_generator
    title = _('Password reset')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        phone_number = form.cleaned_data['phone']
        try:
            user = UserModel.objects.get(phone=phone_number)
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': self.token_generator,
                'request': self.request,
            }
            form.save(**opts)
        except UserModel.DoesNotExist:
            form.add_error(None, 'این شماره موبایل پیدا نشد!')
            return self.form_invalid(form)
        return super().form_valid(form)


# reset password with sending email to user,using PasswordResetView of django and customize it.
class ResetPasswordEmailView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password/password_reset.html'
    email_template_name = 'password/password_reset_email.html'
    subject_template_name = 'password/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('index')


class ContactUpdate(LoginRequiredMixin, View):
    form_class = ContactUpdateForm
    template_name = 'user/contact_update.html'

    def get(self, request, pk, *args, **kwargs):
        contact = Contact.objects.get(pk=pk)
        form = self.form_class(instance=contact)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            update_contact = form.cleaned_data
            contact = Contact.objects.get(pk=pk)
            contact.name = update_contact['name']
            contact.email = update_contact['email']
            contact.phone_number = update_contact['phone_number']
            contact.other_email = update_contact['other_email']
            contact.birth_date = update_contact['birth_date']
            contact.save()
            messages.success(request, 'contact updated successfully', 'success')
            return redirect('contacts')
        return render(request, self.template_name, {'form': form})


class ContactDetail(LoginRequiredMixin, DetailView):
    model = Contact


@login_required(login_url=settings.LOGIN_URL)
def contact_delete(request, pk):
    contact = Contact.objects.filter(id=pk)
    contact.delete()
    messages.success(request, 'contact deleted successfully', 'success')
    return redirect('contacts')


class ContactsOfUser(LoginRequiredMixin, View):
    template_name = 'user/contacts.html'

    def get(self, request):
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        contacts = user.contacts.all()
        # search in name or email of contacts
        form = SearchContactForm()
        if 'search' in request.GET:
            form = SearchContactForm(request.GET)
            if form.is_valid():
                cd = form.cleaned_data['search']
                contacts = contacts.filter(Q(name__icontains=cd) |
                                           Q(phone_number__icontains=cd) |
                                           Q(birth_date__icontains=cd) |
                                           Q(email__username__icontains=cd))
        return render(request, self.template_name, {'contacts': contacts, 'form': form})


class CreateContact(LoginRequiredMixin, View):
    form_class = CreateContactForm
    template_name = 'user/create_contact.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = Users.objects.get(id=request.user.id)
            contact.email = Users.objects.get(username=form.cleaned_data['email'])
            contact.save()
            messages.success(request, 'contact created successfully', 'success')
            return redirect('contacts')
        return render(request, self.template_name, {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def export_to_csv(request):
    model_class = Contact

    meta = model_class._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in model_class.objects.filter(owner_id=request.user):
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response
