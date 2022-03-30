from django.contrib import admin
from mail.models import Email, Category, Signature, Filter
from user.models import Users
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('sender', 'get_recipients', 'get_cc', 'get_bcc',
                    'subject', 'body', 'is_sent',)

    list_filter = ('sender', 'recipients', 'is_sent')

    date_hierarchy = 'created_time'

    search_fields = ('subject', 'body', 'sender')
    # for foreign key fields
    raw_id_fields = ('sender', 'signature', 'reply')
    # for many_to_many fields
    filter_horizontal = ('recipients', 'cc', 'bcc', 'category')

    ordering = ('-created_time', '-sender',)

    readonly_fields = ['created_time', ]

    list_per_page = 10


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name',)
    raw_id_fields = ('owner',)
    fields = ['owner', 'name']

    # Define the default label by admin for all users of website
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            try:
                users = Users.objects.all()
                for user in users:
                    Category.objects.create(owner_id=user.pk, name=request.POST.get("name"))
                return HttpResponseRedirect("/admin/mail/category")
            except Exception as e:
                messages.add_message(request, messages.ERROR, message="This label Exist!")
                return HttpResponseRedirect("/admin/mail/category/add")

        return super(CategoryAdmin, self).add_view(request)


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ('text', 'owner',)
    raw_id_fields = ('owner',)


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ('owner', 'from_user', 'text')
    raw_id_fields = ('owner', 'label')
