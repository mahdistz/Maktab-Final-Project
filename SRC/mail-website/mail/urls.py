from mail.views import CreateCategory, CategoryDetail, EmailDetail, \
    CategoryDelete, InboxMail, DraftMail, AllEmailOfCategory, AddEmailToCategory, Forward, \
    Reply, SentMail, Categories, check_trash, TrashMail, ArchiveMail, check_archive, CreateNewEmail, \
    search_emails, CreateSignature, SignatureDelete, SignatureDetail, Signatures, Settings, Filters, FilterDetail, \
    CreateFilter, filter_delete, api_sent_emails_of_user, api_received_emails_of_user
from django.views.decorators.csrf import csrf_exempt
from django.urls import path

urlpatterns = [
    path('create_new_email/', CreateNewEmail.as_view(), name='create_new_email'),
    path('categories/', Categories.as_view(), name='categories'),
    path('create_category/', CreateCategory.as_view(), name='create_category'),
    path('category_detail/<int:pk>/', CategoryDetail.as_view(), name='category_detail'),
    path('inbox/', InboxMail.as_view(), name='inbox'),
    path('draft/', DraftMail.as_view(), name='draft'),
    path('archive/<int:pk>/', check_archive, name='archive'),
    path('archive/', ArchiveMail.as_view(), name='archives'),
    path('trash/<int:pk>/', check_trash, name='trash'),
    path('trash/', TrashMail.as_view(), name='trashes'),
    path('reply/<int:pk>/', Reply.as_view(), name='reply'),
    path('forward/<int:pk>/', Forward.as_view(), name='forward'),
    path('sent/', SentMail.as_view(), name='sent'),
    path('email_detail/<int:pk>/', EmailDetail.as_view(), name='email_detail'),
    path('category_delete/<int:pk>/', CategoryDelete.as_view(), name='category_delete'),
    path('emails_of_category/<int:pk>/', AllEmailOfCategory.as_view(), name='emails_of_category'),
    path('add_email_to_category/<int:pk>/', AddEmailToCategory.as_view(), name='add_email_to_category'),
    path('search_emails/', csrf_exempt(search_emails), name='search_emails'),
    path('create_signature/', CreateSignature.as_view(), name='create_signature'),
    path('signature_delete/<int:pk>/', SignatureDelete.as_view(), name='signature_delete'),
    path('signature_detail/<int:pk>/', SignatureDetail.as_view(), name='signature_detail'),
    path('signatures/', Signatures.as_view(), name='signatures'),
    path('settings/', Settings.as_view(), name='settings'),
    path('filters/', Filters.as_view(), name='filters'),
    path('filter_detail/<int:pk>/', FilterDetail.as_view(), name='filter_detail'),
    path('create_filter/', CreateFilter.as_view(), name='create_filter'),
    path('filter_delete/<int:pk>/', filter_delete, name='filter_delete'),
    path('api_sent_emails_of_user/', api_sent_emails_of_user, name='api_sent_emails_of_user'),
    path('api_received_emails_of_user/', api_received_emails_of_user, name='api_received_emails_of_user'),
]
