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
from user import views as user_view
from django.contrib.auth import views as auth
from django.conf import settings
from django.conf.urls.static import static
from user.views import SignUpView, ActivateAccount, VerifyCodeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('mail/', include('mail.urls')),
    path('login/', user_view.LoginView.as_view(), name='login'),
    path('logout/', auth.LogoutView.as_view(template_name='user/index.html'), name='logout'),
    path('password_reset/', auth.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_change/', auth.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password/reset/done/', auth.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset/<uid64>/<token>/', auth.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),
    path('register/', SignUpView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),
    # path('register/', user_view.register, name='register'),

] + static(settings.STATIC_URL)
