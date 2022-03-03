import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from utils import send_otp_code, send_otp_code_gh
from .forms import UserRegisterForm, VerifyCodeForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import Users, CodeRegister
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
from mail.forms import CreateMailForm


def index(request):
    return render(request, 'user/index.html', {'title': 'index'})


@login_required(login_url=settings.LOGIN_URL)
def home(request):
    form = CreateMailForm
    return render(request, 'home.html', {'form': form})


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
            return redirect(to='/')
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

                # to show on terminal and complete the request
                print(code)
                # ghasedak service --> error
                # send_otp_code_gh(form.cleaned_data['phone'], code)

                # kavenegar service --> can't send sms because 'sender' is None
                send_otp_code(form.cleaned_data['phone'], code)
                # Sending session to other url for verifying user with sms code.
                request.session['user_registering'] = {
                    'phone': form.cleaned_data['phone'],
                    'email': form.cleaned_data['email'],
                    'password1': form.cleaned_data['password1'],
                    'password2': form.cleaned_data['password2'],
                    'username': form.cleaned_data['username'],
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
