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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sender")

    to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="to")

    cc = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="cc")

    bcc = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="bcc")

    category = models.ManyToManyField(Category, related_name='categories')

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
    is_trashed = models.BooleanField(default=False)
    signature = models.CharField(max_length=100, null=True, blank=True)
    signature_image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f"From: {self.sender}, Sub: {self.subject}"
