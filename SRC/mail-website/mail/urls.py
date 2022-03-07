from mail.views import CreateMail, CategoryList, CreateCategory, CategoryDetail, EmailDetail, EmailList, EmailDelete, \
    CategoryDelete, InboxMail, DraftMail, AllEmailOfCategory
from django.urls import path

urlpatterns = [
    path('new_mail/', CreateMail.as_view(), name='create_mail'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('category_detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('emails/', EmailList.as_view(), name='emails'),
    path('email_detail/<int:pk>/', EmailDetail.as_view(), name='email_detail'),
    path('email_delete/<int:pk>/', EmailDelete.as_view(), name='email_delete'),
    path('category_delete/<int:pk>/', CategoryDelete.as_view(), name='category_delete'),
    path('inbox/', InboxMail.as_view(), name='inbox'),
    path('draft/', DraftMail.as_view(), name='draft'),
    path('emails_of_category/', AllEmailOfCategory.as_view(), name='emails_of_category'),

]
