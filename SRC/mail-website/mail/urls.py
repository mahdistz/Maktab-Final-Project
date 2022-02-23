from django.urls import path

from mail.views import CreateMail

urlpatterns = [
    path('new_mail', CreateMail.as_view(), name='create_mail'),
]
