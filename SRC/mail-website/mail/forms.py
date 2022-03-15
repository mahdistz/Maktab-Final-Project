from django import forms
from mail.models import Email, Category, Signature
from user.models import Users
from django.core import validators
from django.utils.translation import ugettext_lazy as _


class MinLengthValidator(validators.MinLengthValidator):
    message = 'Ensure this value has at least %(limit_value)d elements (it has %(show_value)d).'


class MaxLengthValidator(validators.MaxLengthValidator):
    message = 'Ensure this value has at most %(limit_value)d elements (it has %(show_value)d).'


class CommaSeparatedCharField(forms.Field):
    def __init__(self, dedup=True, max_length=None, min_length=None, *args, **kwargs):
        self.dedup, self.max_length, self.min_length = dedup, max_length, min_length
        super(CommaSeparatedCharField, self).__init__(*args, **kwargs)
        if min_length is not None:
            self.validators.append(MinLengthValidator(min_length))
        if max_length is not None:
            self.validators.append(MaxLengthValidator(max_length))

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return []

        value = [item.strip() for item in value.split(',') if item.strip()]
        if self.dedup:
            value = list(set(value))

        return value

    def clean(self, value):
        value = self.to_python(value)
        self.validate(value)
        self.run_validators(value)
        return value


class CreateMailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'body', 'file', 'signature']

    recipients = CommaSeparatedCharField(max_length=200, required=True)
    cc = CommaSeparatedCharField(max_length=200, required=False)
    bcc = CommaSeparatedCharField(max_length=200, required=False)

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        for receiver in recipients:
            if not Users.objects.filter(username=receiver).exists():
                raise forms.ValidationError(f'there is no user with this email: {receiver}')
        return recipients

    def clean_cc(self):
        cc = self.cleaned_data['cc']
        for receiver in cc:
            if not Users.objects.filter(username=receiver).exists():
                raise forms.ValidationError(f'there is no user with this email: {receiver}')
        return cc

    def clean_bcc(self):
        bcc = self.cleaned_data['bcc']
        for receiver in bcc:
            if not Users.objects.filter(username=receiver).exists():
                raise forms.ValidationError(f'there is no user with this email: {receiver}')
        return bcc

    def clean_file(self):
        if self.cleaned_data['file']:
            file = self.cleaned_data['file']
            if file.size > 25 * 1024 * 1024:
                raise forms.ValidationError('file size should not exceed 25 MB')
            return file


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class AddEmailToCategoryForm(forms.Form):
    name = forms.CharField(max_length=100)


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'body', 'file']


class ForwardForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'body', 'file']

    recipients = CommaSeparatedCharField(max_length=200, required=True)
    cc = CommaSeparatedCharField(max_length=200, required=False)
    bcc = CommaSeparatedCharField(max_length=200, required=False)

    def clean_recipients(self):
        recipients = self.cleaned_data['recipients']
        for receiver in recipients:
            if not Users.objects.filter(username=receiver).exists():
                raise forms.ValidationError(f'there is no user with this email: {receiver}')
        return recipients

    def clean_cc(self):
        cc = self.cleaned_data['cc']
        for receiver in cc:
            if not Users.objects.filter(username=receiver).exists():
                raise forms.ValidationError(f'there is no user with this email: {receiver}')
        return cc

    def clean_bcc(self):
        bcc = self.cleaned_data['bcc']
        for receiver in bcc:
            if not Users.objects.filter(username=receiver).exists():
                raise forms.ValidationError(f'there is no user with this email: {receiver}')
        return bcc


class SignatureForm(forms.ModelForm):
    class Meta:
        model = Signature
        exclude = ['owner']
