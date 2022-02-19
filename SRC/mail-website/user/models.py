from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager
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


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(_('email address'), unique=True)

    mobile_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Mobile Number'),
        validators=[mobile_number_validation],
        error_messages={
            'unique': _("A user with that mobile number already exists."),
        },
        help_text=_('Example') + " : 09125573688")

    birth_date = models.DateField(null=True, blank=True)
    nationality = models.TextField(null=True, blank=True)
    gender_choices = [
        ('f', 'female'),
        ('m', 'male'),
        ('n', 'None'),
    ]
    gender = models.CharField(choices=gender_choices, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
