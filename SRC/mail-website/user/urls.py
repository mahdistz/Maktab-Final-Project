from django.urls import path
from django.contrib.auth import views
from .views import PasswordResetView, index, ActivateAccount, SignUpView, home, VerifyCodeView

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('register/', SignUpView.as_view(), name='register'),
    path('verify/', VerifyCodeView.as_view(), name='verify'),

    # path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
