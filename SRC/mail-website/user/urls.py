from django.urls import path
from .views import index, home, ResetPasswordEmailView, ContactList, CreateContact, ContactDetail, ContactUpdate, \
    ContactDelete

urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('password-reset/', ResetPasswordEmailView.as_view(), name='password_reset'),
    path('contacts/', ContactList.as_view(), name='contacts'),
    path('create_contact/', CreateContact.as_view(), name='create_contact'),
    path('contact_detail/<int:pk>/', ContactDetail.as_view(), name='contact_detail'),
    path('contact_update/<int:pk>/', ContactUpdate.as_view(), name='contact_update'),
    path('contact_delete/<int:pk>/', ContactDelete.as_view(), name='contact_delete'),
]
