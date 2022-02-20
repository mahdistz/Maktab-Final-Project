from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
# from .managers import CustomUserManager
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible


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


@deconstructible
class UsernameValidator(RegexValidator):
    regex = r'^[\w.+-]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./+/-/_ characters.'
    )
    flags = 0


# create an instance from the class
username_validation = UsernameValidator()


class Users(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and ./+/-/_ only.'),
        validators=[username_validation],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    verification_choice = [
        ('Phone', 'Phone Number'),
        ('Email', 'Email')
    ]
    verification = models.CharField(
        max_length=100,
        choices=verification_choice
    )

    phone_number = models.CharField(
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
    nationality = models.TextField(null=True, blank=True)
    gender_choices = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('N', 'None'),
    ]
    gender = models.CharField(max_length=10, choices=gender_choices, null=True, blank=True)
    # is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    # objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.username += '@mail.com'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# class Contact(AbstractUser):
#     contact_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_contact')
