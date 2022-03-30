from django.contrib import admin
from .models import Users, Contact, CodeRegister
from mail.models import Email
from django.db.models import Q
import csv
from django.http import HttpResponse


def size_format(value):
    """
    Simple kb/mb/gb size
    """
    value = int(value)
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
        'export_to_csv',
    ]

    readonly_fields = ['last_login', 'date_joined', 'count_sent_email',
                       'count_received_email']

    list_per_page = 10

    def activate_users(self, request, queryset):
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, 'Activated {} users.'.format(cnt))

    activate_users.short_description = 'Activate Users'

    def count_sent_email(self, obj):
        qs = Email.objects.filter(sender=obj, is_sent=True).exclude(status='total').count()
        return qs

    count_sent_email.short_description = 'Sent Mails'

    def count_received_email(self, obj):
        qs = Email.objects.filter(Q(recipients=obj) | Q(cc=obj) | Q(bcc=obj)).filter(is_filter=False).\
            exclude(status='total').count()
        return qs

    count_received_email.short_description = 'Received Mails'

    def get_user_storage(self, obj):
        # to show on list display
        # downloaded or uploaded file by user
        user_files = Email.objects.filter(Q(sender=obj) | Q(recipients=obj, is_sent=True)) \
            .exclude(Q(file='') | Q(file__isnull=True)).exclude(status='total')
        total = sum(int(objects.file_size) for objects in user_files if objects.file_size)
        total = size_format(total)
        return total

    get_user_storage.short_description = 'Storage Used'

    # override changelist_view method to display chart on admin page
    def changelist_view(self, request, extra_context=None):
        all_emails_with_file = Email.objects.filter(file__isnull=False).exclude(file='')

        usernames = []
        for email in all_emails_with_file:
            usernames.append(Users.objects.get(pk=email.sender_id))
        usernames = list(set(usernames))

        file_data = []
        for user in usernames:
            file_of_user = all_emails_with_file.filter(Q(sender_id=user.id) | Q(recipients=user.id))
            total = sum(int(objects.file_size) for objects in file_of_user if objects.file_size)
            file_data.append({"user": user.username, "user_size": total})

        # attach the file data to the template context
        extra_context = extra_context or {"file_data": file_data}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

    def export_to_csv(self, request, queryset):

        meta = Users._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('owner', 'email',)
    search_fields = ('owner', 'email', 'name',)
    raw_id_fields = ('owner', 'email',)
    ordering = ('-email', '-owner',)


@admin.register(CodeRegister)
class CodeRegisterAdmin(admin.ModelAdmin):
    list_display = ('code', 'phone_number', 'create_at')
