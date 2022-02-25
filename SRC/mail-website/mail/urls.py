from mail.views import CreateMail
from django.urls import path
from . import views

urlpatterns = [
    path('new_mail', CreateMail.as_view(), name='create_mail'),
    # path("", views.index, name="index"),

    ]

