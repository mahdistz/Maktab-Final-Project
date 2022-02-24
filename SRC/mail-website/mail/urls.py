from django.urls import path

from mail.views import CreateMail
from django.urls import path
from . import views

urlpatterns = [
    # path('new_mail', CreateMail.as_view(), name='create_mail'),
    path("", views.index, name="index"),
    # API Routes
    path("emails/", views.compose, name="compose"),
    path("emails/<int:email_id>/", views.email, name="email"),
    path("emails/<str:mailbox>/", views.mailbox, name="mailbox"),
    ]

