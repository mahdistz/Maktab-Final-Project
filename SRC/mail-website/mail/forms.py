from django import forms
from mail.models import Email
from bootstrap_modal_forms.forms import BSModalModelForm


class CreateMailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'body', 'file']


class EmailModelForm(BSModalModelForm):
    class Meta:
        model = Email
        fields = ['sender', 'recipients', 'cc', 'bcc', 'subject', 'body', 'file']
