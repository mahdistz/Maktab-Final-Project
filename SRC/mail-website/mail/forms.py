from django import forms
from mail.models import Email, Category
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
        fields = ['subject', 'body', 'file']

    recipients = CommaSeparatedCharField(max_length=200, required=True)
    cc = CommaSeparatedCharField(max_length=200, required=False)
    bcc = CommaSeparatedCharField(max_length=200, required=False)


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class AddEmailToCategoryForm(forms.Form):
    name = forms.ModelChoiceField(queryset=Category.objects.all())


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
