from mail.views import CreateMail, CreateContact, ContactList, ContactDetail, CategoryList, \
    CreateCategory, CategoryDetail, EmailDetail, EmailList, EmailDelete, ContactUpdate, ContactDelete, \
    CategoryDelete
from django.urls import path

urlpatterns = [
    path('new_mail/', CreateMail.as_view(), name='create_mail'),
    path('contacts/', ContactList.as_view(), name='contacts'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('create_contact/', CreateContact.as_view(), name='create_contact'),
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('contact_detail/<int:pk>/', ContactDetail.as_view(), name='contact_detail'),
    path('category_detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('emails/', EmailList.as_view(), name='emails'),
    path('email_detail/<int:pk>/', EmailDetail.as_view(), name='email_detail'),
    path('email_delete/<int:pk>/', EmailDelete.as_view(), name='email_delete'),
    path('contact_update/<int:pk>/', ContactUpdate.as_view(), name='contact_update'),
    path('contact_delete/<int:pk>/', ContactDelete.as_view(), name='contact_delete'),
    path('category_delete/<int:pk>/', CategoryDelete.as_view(), name='category_delete'),

]
