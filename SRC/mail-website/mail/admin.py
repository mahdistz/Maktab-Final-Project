from django.contrib import admin
from mail.models import Email, Category, Signature, Filter


class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'file', 'created_time', 'is_sent', 'is_trashed', 'is_archived', 'is_read')
    list_filter = ('is_sent', 'is_trashed', 'is_archived', 'is_read')
    date_hierarchy = 'created_time'
    search_fields = ('subject', 'body', 'sender')
    raw_id_fields = ('sender', 'signature', 'reply_to')
    filter_horizontal = ('recipients', 'cc', 'bcc', 'category')
    ordering = ('-created_time', '-sender',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name',)
    list_filter = ('owner', 'name',)
    search_fields = ('owner', 'name',)
    raw_id_fields = ('owner',)


class SignatureAdmin(admin.ModelAdmin):
    list_display = ('text', 'owner',)
    raw_id_fields = ('owner',)


class FilterAdmin(admin.ModelAdmin):
    list_display = ('owner', 'from_user', 'text')
    raw_id_fields = ('owner', 'from_user', 'label')


admin.site.register(Email, EmailAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Signature, SignatureAdmin)
admin.site.register(Filter, FilterAdmin)
