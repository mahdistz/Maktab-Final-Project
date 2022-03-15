from django.urls import path
from .views import index, home, ResetPasswordEmailView, CreateContact, ContactDetail, ContactUpdate, \
    contact_delete, ContactsOfUser, export_to_csv

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('password-reset/', ResetPasswordEmailView.as_view(), name='password_reset'),
    path('contacts/', ContactsOfUser.as_view(), name='contacts'),
    path('export_contact_csv/', export_to_csv, name='export_contact_csv'),
    path('create_contact/', CreateContact.as_view(), name='create_contact'),
    path('contact_detail/<int:pk>/', ContactDetail.as_view(), name='contact_detail'),
    path('contact_update/<int:pk>/', ContactUpdate.as_view(), name='contact_update'),
    path('contact_delete/<int:pk>/', contact_delete, name='contact_delete'),
]
