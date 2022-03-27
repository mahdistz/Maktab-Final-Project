from django.contrib import admin
from .models import Users, Contact, CodeRegister
from mail.models import Email
from django.db.models import Q


def sizify(value):
    """
    Simple kb/mb/gb size:
    """
    # value = ing(value)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'email', 'phone', 'date_joined', 'is_active', 'is_staff', 'count_sent_email',
                    'count_received_email', 'get_user_storage',)

    list_filter = ('is_staff', 'is_active',)

    search_fields = ('username', 'email', 'phone',)

    fieldsets = (
        ('Info',
         {'fields': ('username', 'password', 'verification', 'email', 'phone', 'last_login')}),
        ('Permissions',
         {'fields': ('is_staff', 'is_active')}),
        ('Other Information',
         {'fields': ('first_name', 'last_name', 'date_joined', 'birth_date',
                     'nationality', 'gender')}),
        ('Sent/Received Emails', {'fields': ('count_sent_email',
                                             'count_received_email')}),
    )
    ordering = ('-date_joined', '-username',)

    actions = [
        'activate_users',
    ]

    readonly_fields = ['last_login', 'date_joined', 'count_sent_email',
                       'count_received_email']

    list_per_page = 10

    def activate_users(self, request, queryset):
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, 'Activated {} users.'.format(cnt))

    activate_users.short_description = 'Activate Users'

    def count_sent_email(self, obj):
        qs = Email.objects.filter(sender=obj).count()
        return qs

    count_sent_email.short_description = 'Sent Mails'

    def count_received_email(self, obj):
        qs = Email.objects.filter(Q(recipients=obj) | Q(cc=obj) | Q(bcc=obj)).count()
        return qs

    count_received_email.short_description = 'Received Mails'

    def get_user_storage(self, obj):
        user_files = Email.objects.filter(sender=obj).exclude(file=None)
        total = sum(int(objects.file_size) for objects in user_files if objects.file_size)
        total = sizify(total)
        return total

    get_user_storage.short_description = 'Storage Used'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('owner', 'email',)
    search_fields = ('owner', 'email', 'name',)
    raw_id_fields = ('owner', 'email',)
    ordering = ('-email', '-owner',)


@admin.register(CodeRegister)
class CodeRegisterAdmin(admin.ModelAdmin):
    list_display = ('code', 'phone_number', 'create_at')
