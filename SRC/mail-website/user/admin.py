from django.contrib import admin
from .models import Users, Contact, CodeRegister


class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone',)
    list_filter = ('email', 'is_staff', 'is_active',)
    search_fields = ('first_name', 'last_name', 'username', 'email', 'phone')
    fieldsets = (
        ('Info', {'fields': ('username', 'verification', 'email', 'phone', 'last_login')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Other Information', {'fields': ('first_name', 'last_name', 'date_joined', 'birth_date',
                                          'nationality', 'gender')}),
    )
    ordering = ('-date_joined', '-username',)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('owner', 'email',)
    list_filter = ('owner', 'email', 'name',)
    search_fields = ('owner', 'email', 'name',)
    raw_id_fields = ('owner', 'email',)
    ordering = ('-email', '-owner',)


class CodeRegisterAdmin(admin.ModelAdmin):
    list_display = ('code', 'phone_number','create_at')


admin.site.register(Users, UsersAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(CodeRegister, CodeRegisterAdmin)
