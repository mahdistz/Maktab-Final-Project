from django.urls import path
from .views import index, home, ResetPasswordEmailView

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('password-reset/', ResetPasswordEmailView.as_view(), name='password_reset'),
]