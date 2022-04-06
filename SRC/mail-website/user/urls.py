from django.urls import path
from .views import index, home, ResetPasswordEmailView, CreateContact, ContactDetail, ContactUpdate, \
    contact_delete, ContactsOfUser, export_to_csv, api_contacts_of_user, SendEmailToContact, forgot_password, \
    ResetPasswordPhoneView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('password-reset/', ResetPasswordEmailView.as_view(), name='password_reset'),
    path('password-reset-phone/', ResetPasswordPhoneView.as_view(), name='password_reset_phone'),
    path('contacts/', ContactsOfUser.as_view(), name='contacts'),
    path('export_contact_csv/', export_to_csv, name='export_contact_csv'),
    path('create_contact/', CreateContact.as_view(), name='create_contact'),
    path('contact_detail/<int:pk>/', ContactDetail.as_view(), name='contact_detail'),
    path('contact_update/<int:pk>/', ContactUpdate.as_view(), name='contact_update'),
    path('contact_delete/<int:pk>/', contact_delete, name='contact_delete'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('api_contacts_of_user/', api_contacts_of_user, name='api_contacts_of_user'),
    path('send_email_to_contact/<int:pk>/', SendEmailToContact.as_view(), name='send_email_to_contact'),

]
