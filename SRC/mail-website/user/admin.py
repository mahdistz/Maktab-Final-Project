from django.contrib import admin
from .models import Users, Contact, CodeRegister
from mail.models import Email
from django.db.models import Q


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name',
                    'email', 'phone', 'date_joined', 'is_active', 'is_staff', 'count_sent_email',
                    'count_received_email')

    list_filter = ('is_staff', 'is_active',)

    search_fields = ('username', 'email', 'phone')

    fieldsets = (
        ('Info',
         {'fields': ('username', 'password', 'verification', 'email', 'phone', 'last_login')}),
        ('Permissions',
         {'fields': ('is_staff', 'is_active')}),
        ('Other Information',
         {'fields': ('first_name', 'last_name', 'date_joined', 'birth_date',
                     'nationality', 'gender')}),
    )
    ordering = ('-date_joined', '-username',)

    actions = [
        'activate_users',
    ]

    readonly_fields = ['last_login', 'date_joined']

    list_per_page = 10

    def activate_users(self, request, queryset):
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, 'Activated {} users.'.format(cnt))

    activate_users.short_description = 'Activate Users'

    def count_sent_email(self, obj):
        qs = Email.objects.filter(sender=obj).count()
        return qs

    count_sent_email.short_description = 'Sent Mails No'

    def count_received_email(self, obj):
        qs = Email.objects.filter(Q(recipients=obj) | Q(cc=obj) | Q(bcc=obj)).count()
        return qs

    count_received_email.short_description = 'Received Mails No'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('owner', 'email',)
    search_fields = ('owner', 'email', 'name',)
    raw_id_fields = ('owner', 'email',)
    ordering = ('-email', '-owner',)


@admin.register(CodeRegister)
class CodeRegisterAdmin(admin.ModelAdmin):
    list_display = ('code', 'phone_number', 'create_at')
