from django.contrib import admin
from mail.models import Email, Category, Signature, Filter


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):

    list_display = ('sender', 'get_recipients', 'get_cc', 'get_bcc',
                    'subject', 'body', 'is_sent',)

    list_filter = ('sender', 'recipients',)

    date_hierarchy = 'created_time'

    search_fields = ('subject', 'body', 'sender')
    # for foreign key fields
    raw_id_fields = ('sender', 'signature', 'reply_to')
    # for many_to_many fields
    filter_horizontal = ('recipients', 'cc', 'bcc', 'category')

    ordering = ('-created_time', '-sender',)

    readonly_fields = ['created_time', ]

    list_per_page = 10


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name',)
    raw_id_fields = ('owner',)


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('text', 'owner',)
    raw_id_fields = ('owner',)


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ('owner', 'from_user', 'text')
    raw_id_fields = ('owner', 'from_user', 'label')
