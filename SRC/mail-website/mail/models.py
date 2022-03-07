from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


def file_validator(value):
    limit = 25 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 25 MiB.')


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<sender.username>/<filename>
    return '{0}/{1}'.format(instance.sender.username, filename)


class Category(models.Model):
    name = models.CharField(max_length=100)


# Create your models here.
class Email(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sender")

    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="to")

    cc = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="cc")

    bcc = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="bcc")

    category = models.ManyToManyField(Category, blank=True, related_name='categories')

    subject = models.CharField(max_length=255, null=True, blank=True)

    body = models.TextField(blank=True, null=True)

    created_time = models.DateTimeField(auto_now_add=True)

    file = models.FileField(null=True,
                            blank=True,
                            upload_to=user_directory_path,
                            help_text='max 25 megabytes',
                            validators=[file_validator],
                            )

    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    is_trashed = models.BooleanField(default=False)
    signature = models.CharField(max_length=100, null=True, blank=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_time']

    def __str__(self):
        return f"From: {self.sender}, Sub: {self.subject}"
