from django import forms

from mail.models import Email


class CreateMailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['sender', 'recipients', 'subject', 'body', 'file']
