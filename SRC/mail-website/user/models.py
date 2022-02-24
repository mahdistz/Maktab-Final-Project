from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, ValidationError
from django.utils.deconstruct import deconstructible
from .managers import CustomUserManager
import re


@deconstructible
class MobileNumberValidator(RegexValidator):
    # A rejection to check user input information
    regex = r"^[0][9]\d{9}$"

    message = _(
        'Enter a valid mobile number. This value may contain only numbers.'
    )
    flags = 0


# create an instance from the class
mobile_number_validation = MobileNumberValidator()


def username_validation(username_str):
    result = re.search('@mail.com$', username_str)
    if result:
        raise ValidationError('username should be without domain')


class Users(AbstractUser):
    username_validator_django = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator_django, username_validation],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    verification_choice = [
        ('Phone', 'Phone'),
        ('Email', 'Email')
    ]
    verification = models.CharField(default='',
                                    max_length=100,
                                    choices=verification_choice
                                    )
    phone = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Phone Number'),
        validators=[mobile_number_validation],
        error_messages={
            'unique': _("A user with that Phone number already exists."),
        },
        help_text=_('Example') + " : 09125573688")

    email = models.EmailField(_('email address'), unique=True)

    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    gender_choices = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('N', 'None'),
    ]
    gender = models.CharField(max_length=10, choices=gender_choices, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='main_user')
    contact = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='contact_user')


class CodeRegister(models.Model):
    code = models.IntegerField()
    phone_number = models.CharField(max_length=11, default='')
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}"
