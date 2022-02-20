from django.contrib import admin

# Register your models here.
from mail.models import Email, Category

admin.site.register(Email)
admin.site.register(Category)
