from django import forms

from mail.models import Email


class CreateMailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['sender', 'to', 'subject', 'body', 'file']
