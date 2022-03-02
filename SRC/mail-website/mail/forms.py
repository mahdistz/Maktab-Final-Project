from django import forms
from mail.models import Email, Category
from user.models import Contact


class CreateMailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['recipients', 'cc', 'bcc', 'subject', 'body', 'file']


class CreateContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
