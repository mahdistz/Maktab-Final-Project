"""SRC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from mail.views import EmailCreateView
from user.forms import LoginForm
from user.views import SignUpView, ActivateAccount, VerifyCodeView, LoginView, CustomLoginView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('user.urls')),
                  path('mail/', include('mail.urls')),
                  path('create/', EmailCreateView.as_view(), name='create_email'),
                  path('password-reset-confirm/<uidb64>/<token>/',
                       auth.PasswordResetConfirmView.as_view(template_name='password/password_reset_confirm.html'),
                       name='password_reset_confirm'),
                  path('password-reset-complete/',
                       auth.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
                       name='password_reset_complete'),
                  path('login/',
                       CustomLoginView.as_view(redirect_authenticated_user=True, template_name='user/login.html',
                                               authentication_form=LoginForm), name='login'),
                  path('logout/', auth.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
                  path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
                  path('register/', SignUpView.as_view(), name='register'),
                  path('verify/', VerifyCodeView.as_view(), name='verify'),
                  # path('register/', user_view.register, name='register'),

              ] + static(settings.STATIC_URL)
