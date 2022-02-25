import random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.views import View
from utils import send_otp_code, send_otp_code_gh
from .forms import UserRegisterForm, VerifyCodeForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
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


def index(request):
    return render(request, 'user/index.html', {'title': 'index'})


@login_required(login_url=settings.LOGIN_URL, redirect_field_name='next')
def home(request):
    return render(request, 'website-menu/index.html')


# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             email = form.cleaned_data.get('email')
#             # mail
#             htmly = get_template('user/acc_active_email.html')
#             d = {'username': username}
#             subject, from_email, to = 'welcome', 'mahdis.taghizadeh1376@gmail.com', email
#             html_content = htmly.render(d)
#             msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
#             msg.attach_alternative(html_content, "text/html")
#             msg.send()
#
#             messages.success(request, f'Your account has been created ! You are now able to log in')
#             return redirect('login')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'user/register.html', {'form': form, 'title': 'register here'})


class LoginView(View):
    template_name = 'user/login.html'
    # template_name = 'login/index.html'

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f' welcome {username}')
            return redirect('index')
        else:
            messages.info(request, f'account done not exit please sign in')

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form, 'title': 'log in'})


class SignUpView(View):
    form_class = UserRegisterForm
    # template_name = 'register/index.html'
    template_name = 'user/register.html'

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
                code = random.randint(1000, 9999)
                CodeRegister.objects.create(phone_number=form.cleaned_data['phone'],
                                            code=code)

                # to show on terminal and complete the request
                print(code)
                # ghasedak service --> error
                # send_otp_code_gh(form.cleaned_data.get('phone_number'), code)

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
                messages.success(request, 'we sent you a code')
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


class PasswordResetView(PasswordContextMixin, FormView):
    form_class = PasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'
    token_generator = default_token_generator
    title = _('Password reset')

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        phone_number = form.cleaned_data['phone_number']
        try:
            user = UserModel.objects.get(phone_number=phone_number)
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
