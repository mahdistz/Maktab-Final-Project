from django.contrib import admin
from .models import Users, Contact, CodeRegister
from mail.models import Email
from django.utils.html import mark_safe


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone')
    list_filter = ('email', 'is_staff', 'is_active',)
    search_fields = ('first_name', 'last_name', 'username', 'email', 'phone')
    fieldsets = (
        ('Info', {'fields': ('username', 'verification', 'email', 'phone', 'last_login')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('Other Information', {'fields': ('first_name', 'last_name', 'date_joined', 'birth_date',
                                          'nationality', 'gender')}),
    )
    ordering = ('-date_joined', '-username',)
    inlines = [EmailInline]

    actions = [
        'activate_users',
        'show_all_users'
    ]
    list_per_page = 10

    def activate_users(self, request, queryset):
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, 'Activated {} users.'.format(cnt))

    activate_users.short_description = 'Activate Users'  # type: ignore


class ContactAdmin(admin.ModelAdmin):
    list_display = ('owner', 'email',)
    list_filter = ('owner', 'email', 'name',)
    search_fields = ('owner', 'email', 'name',)
    raw_id_fields = ('owner', 'email',)
    ordering = ('-email', '-owner',)


class CodeRegisterAdmin(admin.ModelAdmin):
    list_display = ('code', 'phone_number', 'create_at')


admin.site.register(Users, UsersAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(CodeRegister, CodeRegisterAdmin)
