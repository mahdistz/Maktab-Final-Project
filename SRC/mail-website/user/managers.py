from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


# manager for create user and superuser with username and password
class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, phone, email, **extra_fields):
        """
        Create and save a Users with the given username and password.
        """
        if not username:
            raise ValueError(_('The username must be set'))
        username = self.normalize_username(username)
        username = username + '@mail.com'
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUsers with the given username and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(username, password, **extra_fields)

    def normalize_username(self, username):
        return username

# manager for create user and superuser with phone and password
#
# class UserManager(BaseUserManager):
#
#     def create_user(self, mobile_number, password=None, **extra_fields):
#         if not mobile_number:
#             raise ValueError(_('The mobile number must be set'))
#         mobile_number = self.normalize_mobile_number(mobile_number)
#         user = self.model(mobile_number=mobile_number, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user
#
#     def create_staff_user(self, mobile_number, password):
#         user = self.create_user(
#             mobile_number,
#             password=password,
#         )
#         user.is_staff = True
#         user.save()
#         return user
#
#     def create_superuser(self, mobile_number, password):
#         user = self.create_user(
#             mobile_number,
#             password=password,
#         )
#         user.is_staff = True
#         user.is_superuser = True
#         user.save()
#         return user
#
#     def normalize_mobile_number(self, mobile_number):
#         return mobile_number
