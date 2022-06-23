from django.urls import path, include
from rest_framework import routers
from .views import index, home, ResetPasswordEmailView, CreateContact, ContactDetail, ContactUpdate, \
    contact_delete, ContactsOfUser, export_to_csv, ContactsOfUserAPI, SendEmailToContact, forgot_password, \
    ResetPasswordPhoneView
from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()
router.register('contacts_of_user/', ContactsOfUserAPI, basename='contacts_of_user')

urlpatterns = [

    # urls for api
    path('api/', include(router.urls)),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # urls for user
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('forgot_password/', forgot_password, name='forgot_password'),
    path('password-reset/', ResetPasswordEmailView.as_view(), name='password_reset'),
    path('password-reset-phone/', ResetPasswordPhoneView.as_view(), name='password_reset_phone'),

    # urls for contacts
    path('create_contact/', CreateContact.as_view(), name='create_contact'),
    path('contact_detail/<int:pk>/', ContactDetail.as_view(), name='contact_detail'),
    path('contact_update/<int:pk>/', ContactUpdate.as_view(), name='contact_update'),
    path('contact_delete/<int:pk>/', contact_delete, name='contact_delete'),
    path('send_email_to_contact/<int:pk>/', SendEmailToContact.as_view(), name='send_email_to_contact'),
    path('contacts/', ContactsOfUser.as_view(), name='contacts'),
    path('export_contact_csv/', export_to_csv, name='export_contact_csv'),

]
