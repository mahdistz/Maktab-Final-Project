from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

#
# class CustomUserManager(BaseUserManager):
#     """
#     Custom user model manager where email is the unique identifiers
#     for authentication instead of usernames.
#     """
#
#     def create_user(self, email, password, **extra_fields):
#         """
#         Create and save a Users with the given email and password.
#         """
#         if not email:
#             raise ValueError(_('The Email must be set'))
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save()
#         return user
#
#     def create_superuser(self, email, password, **extra_fields):
#         """
#         Create and save a SuperUser with the given email and password.
#         """
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(_('Superuser must have is_staff=True.'))
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError(_('Superuser must have is_superuser=True.'))
#         return self.create_user(email, password, **extra_fields)
#
#
# ##################################################################################
#
# class UserManager(BaseUserManager):
#     use_in_migrations = True  # migration سریالایز کردن منیجر در
#
#     def create_user(self, mobile_number, password=None, **extra_fields):
#         if not mobile_number:
#             raise ValueError(_('The mobile number must be set'))
#         mobile_number = self.normalize_mobile_number(mobile_number)
#         user = self.model(mobile_number=mobile_number, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#
#     def create_staff_user(self, mobile_number, password):
#         user = self.create_user(
#             mobile_number,
#             password=password,
#         )
#         user.is_staff = True
#         user.save(using=self._db)
#         return user
#
#     def create_superuser(self, mobile_number, password):
#         user = self.create_user(
#             mobile_number,
#             password=password,
#         )
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user
#
#     def normalize_mobile_number(self, mobile_number):
#         return mobile_number
