from django.conf import settings
from django.db import models
from user.models import Users
from django.core.exceptions import ValidationError


def file_validator(value):
    limit = 25 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 25 MiB.')


class Category(models.Model):
    name = models.CharField(max_length=100)


# Create your models here.
class Email(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="emails")

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="emails_sent")

    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="emails_received")

    category = models.ManyToManyField(Category, related_name='mail_category')

    subject = models.CharField(max_length=255, null=True, blank=True)

    body = models.TextField(blank=True, null=True)

    created_time = models.DateTimeField(auto_now_add=True)

    file = models.FileField(null=True,
                            blank=True,
                            upload_to='documents/%Y/%m/%d',
                            help_text='max 25 megabytes',
                            validators=[file_validator]
                            )

    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_drafted = models.BooleanField(default=False)
    is_trashed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id": self.id,
            "sender": self.sender.email,
            "recipients": [user.email for user in self.recipients.all()],
            "subject": self.subject,
            "body": self.body,
            "created_time": self.created_time.strftime("%b %d %Y, %I:%M %p"),
            "is_read": self.is_read,
            "is_sent": self.is_sent,
            "is_starred": self.is_starred,
            "is_archived": self.is_archived,
            "file": self.file,
            "is_drafted": self.is_drafted,
            "is_trashed": self.is_trashed,
            "is_deleted": self.is_deleted,

        }

    def __str__(self):
        return f"From: {self.sender}, Sub: {self.subject}"
