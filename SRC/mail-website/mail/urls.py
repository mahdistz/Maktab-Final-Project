from mail.views import CreateMail
from django.urls import path
from .views import index,compose,email,mailbox

urlpatterns = [
    # path('new_mail', CreateMail.as_view(), name='create_mail'),
    # path("", views.index, name="index"),
    path("", index, name="index"),

    # API Routes
    path("emails/", compose, name="compose"),
    path("emails/<int:email_id>/", email, name="email"),
    path("emails/<str:mailbox>/", mailbox, name="mailbox"),
    ]

