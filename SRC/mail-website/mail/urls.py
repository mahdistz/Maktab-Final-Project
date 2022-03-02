from mail.views import CreateMail, CreateContact, ContactList, ContactDetail, CategoryList, \
    CreateCategory, CategoryDetail
from django.urls import path

urlpatterns = [
    path('new_mail/', CreateMail.as_view(), name='create_mail'),
    # path('new_email/', EmailCreateView.as_view(), name='create_email'),
    path('contacts/', ContactList.as_view(), name='contacts'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('create_contact/', CreateContact.as_view(), name='create_contact'),
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('contact_detail/<int:pk>/', ContactDetail.as_view(), name='contact_detail'),
    path('category_detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),

]
