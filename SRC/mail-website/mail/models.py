from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField


def file_validator(value):
    limit = 25 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 25 MiB.')


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<sender.username>/<filename>
    return '{0}/{1}'.format(instance.sender.username, filename)


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, default='', on_delete=models.CASCADE, related_name="owner_category")

    class Meta:
        unique_together = [('name', 'owner')]

    def __str__(self):
        return f"{self.name}"


class Signature(models.Model):
    text = models.CharField(max_length=100, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owner_signature")

    def __str__(self):
        return f"{self.text}"


class Filter(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owner_filter")
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='from', on_delete=models.PROTECT, related_name="from_user", null=True,
        blank=True)
    text = models.CharField(max_length=100, verbose_name='text', null=True, blank=True)
    label = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="label", null=True, blank=True)


class Email(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sender")

    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="to")

    cc = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="cc")

    bcc = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="bcc")

    category = models.ManyToManyField(Category, blank=True, related_name='categories')

    subject = models.CharField(max_length=255, null=True, blank=True)

    # body = models.TextField(blank=True, null=True)
    body = RichTextUploadingField(blank=True, null=True)

    created_time = models.DateTimeField(auto_now_add=True)

    file = models.FileField(null=True,
                            blank=True,
                            upload_to=user_directory_path,
                            help_text='max 25 megabytes',
                            validators=[file_validator],
                            )

    is_sent = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_trashed = models.BooleanField(default=False)
    status_choices = [
        ('recipients', 'recipients'),
        ('cc', 'cc'),
        ('bcc', 'bcc'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='')
    signature = models.ForeignKey(Signature, on_delete=models.CASCADE, null=True, blank=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_time']

    def __str__(self):
        return f"From: {self.sender}, Sub: {self.subject}"

    def get_recipients(self):
        return "\n".join([p.username for p in self.recipients.all()])

    def get_cc(self):
        return "\n".join([p.username for p in self.cc.all()])

    def get_bcc(self):
        return "\n".join([p.username for p in self.bcc.all()])

