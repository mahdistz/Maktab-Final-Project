from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import Email, Category, Signature, Filter
from user.models import Users
from mail.forms import CreateMailForm, CreateCategoryForm, \
    AddEmailToCategoryForm, ForwardForm, ReplyForm, SignatureForm, CreateFilterForm
from django.urls import reverse_lazy
from django.views.generic import DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view  # GET PUT POST , ..... نوع درخواست
from rest_framework.response import Response  # ارسال پاسخ ها
from .serializers import EmailSerializer
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger('mail')


@csrf_exempt
@api_view(["GET"])
def api_sent_emails_of_user(request):
    user = Users.objects.get(id=request.user.id)
    emails = Email.objects.filter(sender=user, is_sent=True, is_archived=False, is_trashed=False,
                                  is_filter=False).exclude(status='total')
    serializer = EmailSerializer(emails, many=True)
    return Response(serializer.data)


@csrf_exempt
@api_view(["GET"])
def api_received_emails_of_user(request):
    user = Users.objects.get(id=request.user.id)
    emails = Email.objects.filter(
        Q(recipients=user, status='recipients', is_archived=False, is_trashed=False, is_filter=False) |
        Q(recipients=user, status='cc', is_archived=False, is_trashed=False, is_filter=False) |
        Q(recipients=user, status='bcc', is_archived=False, is_trashed=False, is_filter=False))
    serializer = EmailSerializer(emails, many=True)
    return Response(serializer.data)


@login_required(login_url=settings.LOGIN_URL)
def search_emails(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        emails = Email.objects.filter(Q(body__icontains=search_str, recipients=request.user) |
                                      Q(body__icontains=search_str, cc=request.user) |
                                      Q(body__icontains=search_str, bcc=request.user) |
                                      Q(body__icontains=search_str, sender=request.user))
        data = emails.values()
        for email in data:
            email['sender_id'] = Users.objects.get(pk=email['sender_id']).username
            email['created_time'] = email['created_time'].strftime('%Y-%m-%d %H:%M:%S')
        return JsonResponse(list(data), safe=False)


class CreateSignature(LoginRequiredMixin, View):
    form_class = SignatureForm
    template_name = 'mail/create_signature.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            signature = form.save(commit=False)
            owner = Users.objects.get(id=request.user.id)
            signature.owner = owner
            signature.save()
            messages.success(request, 'signature saved successfully', 'success')
            return redirect('signatures')
        messages.error(request, 'signature does not create', 'error')
        logger.error('signature does not create')
        return render(request, self.template_name, {'form': form})


class SignatureDetail(LoginRequiredMixin, DetailView):
    model = Signature


class SignatureDelete(LoginRequiredMixin, DeleteView):
    model = Signature
    success_url = reverse_lazy('signatures')


class Signatures(LoginRequiredMixin, View):
    template_name = 'mail/signatures.html'

    def get(self, request):
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        signatures = Signature.objects.filter(owner=user)
        return render(request, self.template_name, {'signatures': signatures})


def to_cc_bcc(to, cc, bcc):
    all_receiver = []

    all_receiver.extend(to)

    if cc is not None:
        all_receiver.extend(cc)

    if bcc is not None:
        all_receiver.extend(bcc)

    return all_receiver


class CreateNewEmail(LoginRequiredMixin, View):
    form_class = CreateMailForm
    template_name = 'mail/create_new_email.html'

    def get(self, request):
        form = self.form_class
        owner = Users.objects.get(id=request.user.id)
        signatures = Signature.objects.filter(owner=owner)
        return render(request, self.template_name, {'form': form, 'signatures': signatures})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        form.subject = request.POST.get('subject')
        form.file = request.POST.get('file')
        form.body = request.POST.get('body')
        form.recipients = request.POST.get('recipients')
        form.cc = request.POST.get('cc')
        form.bcc = request.POST.get('bcc')
        if request.POST.get('text'):
            form.signature = request.POST.get('text')
        if form.is_valid():
            owner = Users.objects.get(id=request.user.id)
            if request.POST.get('text'):
                signature = Signature.objects.get(owner=owner, text=form.signature)
            if 'save' in request.POST:
                # When the user presses the save button, email's field is_sent=True,
                # then email object saved.
                cd = form.cleaned_data
                to_cc_bcc_list = to_cc_bcc(cd['recipients'], cd['cc'], cd['bcc'])
                # Clear duplicates receiver
                receiver_list = list(dict.fromkeys(to_cc_bcc_list))
                sender = Users.objects.get(id=request.user.id)
                # create one object of email with all recipients,cc,bc and
                # status total to save all data in one object
                total_email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                   body=cd['body'], file=cd['file'],
                                                   is_sent=True, status='total')
                if request.POST.get('text'):
                    total_email.signature = signature

                for receiver in receiver_list:
                    if receiver in cd['recipients']:
                        recipients = Users.objects.get_by_natural_key(username=receiver)
                        total_email.recipients.add(recipients)

                    elif receiver in cd['cc']:
                        cc_people = Users.objects.get_by_natural_key(username=receiver)
                        total_email.cc.add(cc_people)

                    elif receiver in cd['bcc']:
                        bcc_people = Users.objects.get_by_natural_key(username=receiver)
                        total_email.bcc.add(bcc_people)

                total_email.save()

                # create one object email for each receiver
                for receiver in receiver_list:
                    if receiver in cd['recipients']:

                        email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                     body=cd['body'], file=cd['file'],
                                                     is_sent=True, status='recipients')
                        if request.POST.get('text'):
                            email.signature = signature

                        recipients = Users.objects.get_by_natural_key(username=receiver)
                        email.recipients.add(recipients)
                        email.save()

                    elif receiver in cd['cc']:

                        email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                     body=cd['body'], file=cd['file'],
                                                     is_sent=True, status='cc')
                        if request.POST.get('text'):
                            email.signature = signature

                        recipients = Users.objects.get_by_natural_key(username=receiver)
                        email.recipients.add(recipients)
                        email.save()

                    elif receiver in cd['bcc']:

                        email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                     body=cd['body'], file=cd['file'],
                                                     is_sent=True, status='bcc')
                        if request.POST.get('text'):
                            email.signature = signature

                        recipients = Users.objects.get_by_natural_key(username=receiver)
                        email.recipients.add(recipients)
                        email.save()

                messages.success(request, 'mail sent successfully', 'success')
                return redirect('sent')

            if 'cancel' in request.POST:
                # When the user presses the cancel button, email's field is_sent=False (by default),
                # and email object saved. save with is_sent = False to show email on Draft
                cd = form.cleaned_data
                sender = Users.objects.get(id=request.user.id)
                email = Email.objects.create(sender=sender, subject=cd['subject'], file=cd['file']
                                             , body=cd['body'])
                if request.POST.get('text'):
                    email.signature = signature

                for people in cd['recipients']:
                    recipients = Users.objects.get_by_natural_key(username=people)
                    email.recipients.add(recipients)

                if cd['cc']:
                    for people in cd['cc']:
                        cc_receiver = Users.objects.get_by_natural_key(username=people)
                        email.cc.add(cc_receiver)

                if cd['bcc']:
                    for people in cd['bcc']:
                        bcc_receiver = Users.objects.get_by_natural_key(username=people)
                        email.bcc.add(bcc_receiver)

                email.save()

                messages.info(request, 'Email saved in draft', 'info')
                return redirect('draft')

        else:
            messages.error(request, "Email could not be sent", 'error')
            logger.error("Email could not be sent")
            return render(request, 'mail/create_new_email.html', {'form': form})


class CategoryDetail(LoginRequiredMixin, DetailView):
    model = Category


class Categories(LoginRequiredMixin, View):
    template_name = 'mail/categories.html'

    def get(self, request):
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        categories = Category.objects.filter(owner=user)
        return render(request, self.template_name, {'categories': categories})


class AllEmailOfCategory(LoginRequiredMixin, View):
    template_name = 'mail/all_email_of_category.html'

    def get(self, request, pk):
        category = Category.objects.get(pk=pk)
        emails = Email.objects.filter(category__owner=request.user, category__exact=category)
        return render(request, self.template_name, {'emails': emails, 'category': category})


class CreateCategory(LoginRequiredMixin, View):
    form_class = CreateCategoryForm
    template_name = 'mail/create_category.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.owner = Users.objects.get(id=request.user.id)
            # checking unique_together for name and owner
            if Category.objects.filter(owner=request.user, name=category.name).exists():
                messages.error(request, f'dear {request.user},you can not create two label with same name ', 'error')
                logger.error(f'{request.user} can not create two label with same name ')
                return redirect('create_category')
            else:
                category.save()
                messages.success(request, 'label created successfully', 'success')
                return redirect('categories')
        messages.error(request, 'label not created ', 'error')
        logger.error('label not created ')
        return render(request, self.template_name, {'form': form})


class AddEmailToCategory(LoginRequiredMixin, View):
    form_class = AddEmailToCategoryForm
    template_name = 'mail/add_email_to_category.html'

    def get(self, request, pk):
        form = self.form_class
        owner = Users.objects.get(id=request.user.id)
        categories = Category.objects.filter(owner=owner)
        return render(request, self.template_name, {'form': form, 'categories': categories})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        form.name = request.POST.get('name')
        if form.is_valid():
            email = Email.objects.get(pk=pk)
            category_obj = Category.objects.get(name=form.cleaned_data['name'], owner=request.user)
            email.category.add(category_obj)
            email.save()
            messages.success(request, 'Email added to the label successfully', 'success')
            return redirect('categories')
        messages.error(request, ' Email not added to the label', 'error')
        logger.error('Email not added to the label')
        return render(request, self.template_name, {'form': form})


class EmailDetail(LoginRequiredMixin, DetailView):
    model = Email


class InboxMail(LoginRequiredMixin, View):
    template_name = 'mail/inbox.html'

    def get(self, request):

        # Get all emails sent to the user from the database
        emails = Email.objects.filter(
            Q(recipients=request.user.id, status='recipients', is_archived=False, is_trashed=False, is_filter=False) |
            Q(recipients=request.user.id, status='cc', is_archived=False, is_trashed=False, is_filter=False) |
            Q(recipients=request.user.id, status='bcc', is_archived=False, is_trashed=False, is_filter=False)).order_by(
            '-created_time')
        # Check emails with user-defined filters. Changes apply if filter exists
        filters = Filter.objects.filter(owner_id=request.user.id)
        if filters:
            for filter_obj in filters:
                if filter_obj.from_user:

                    from_user = Users.objects.get(username=filter_obj.from_user)
                    for email in emails.filter(sender=from_user):

                        if filter_obj.trash_or_archive == 'Archive':
                            email.is_archived = True

                        elif filter_obj.trash_or_archive == 'Trash':
                            email.is_trashed = True

                        elif filter_obj.label:
                            label = Category.objects.get(name=filter_obj.label, owner=request.user)
                            email.category.add(label)

                        email.is_filter = True
                        email.save()

                if filter_obj.text:
                    for email in emails.filter(Q(body__icontains=filter_obj.text) |
                                               Q(subject__icontains=filter_obj.text)):

                        if filter_obj.trash_or_archive == 'Archive':
                            email.is_archived = True

                        elif filter_obj.trash_or_archive == 'Trash':
                            email.is_trashed = True

                        elif filter_obj.label:
                            label = Category.objects.get(name=filter_obj.label, owner=request.user)
                            email.category.add(label)

                        email.is_filter = True
                        email.save()
        # notification to user when user is login and received new mail
        user = request.user
        for email in emails:
            if email.created_time >= user.last_login:
                messages.info(request, 'you have one new email')

        return render(request, self.template_name, {'emails': emails})


class SentMail(LoginRequiredMixin, View):
    template_name = 'mail/sent.html'

    def get(self, request):
        sent = Email.objects.filter(sender__exact=request.user.id,
                                    is_sent=True, is_archived=False, is_trashed=False, status='total')
        return render(request, self.template_name, {'sent': sent})


class DraftMail(LoginRequiredMixin, View):
    template_name = 'mail/draft.html'

    def get(self, request):
        drafts = Email.objects.filter(sender=request.user.id,
                                      is_sent=False, is_archived=False, is_trashed=False).exclude(status='total')
        return render(request, self.template_name, {'drafts': drafts})


@login_required(login_url=settings.LOGIN_URL)
def check_archive(request, pk):
    if request.method == 'GET':

        email = Email.objects.get(pk=pk)
        if not email.is_archived:
            email.is_archived = True
            messages.info(request, 'email moved to Archive ', 'info')

        elif email.is_archived:
            email.is_archived = False
            messages.info(request, 'email un-archived ', 'info')

        email.save()
        return redirect('archives')


class ArchiveMail(LoginRequiredMixin, View):
    template_name = 'mail/archive.html'

    def get(self, request):
        user = Users.objects.get(id=request.user.id)
        archives = Email.objects.filter(Q(recipients=user, is_archived=True) |
                                        Q(cc=user, is_archived=True) |
                                        Q(bcc=user, is_archived=True) |
                                        Q(sender=user, is_archived=True)).exclude(
            status='total').order_by('-created_time')

        return render(request, self.template_name, {'archives': archives})


@login_required(login_url=settings.LOGIN_URL)
def check_trash(request, pk):
    if request.method == 'GET':

        email = Email.objects.get(pk=pk)
        if not email.is_trashed:
            email.is_trashed = True
            messages.info(request, 'email moved to Trash ', 'info')

        elif email.is_trashed:
            email.is_trashed = False
            messages.info(request, 'email un-trashed ', 'info')
        email.save()
        return redirect('trashes')


class TrashMail(LoginRequiredMixin, View):
    template_name = 'mail/trash.html'

    def get(self, request):
        user = Users.objects.get(id=request.user.id)
        trashes = Email.objects.filter(
            Q(recipients=user, is_trashed=True, is_archived=False) |
            Q(cc=user, is_trashed=True, is_archived=False) |
            Q(bcc=user, is_trashed=True, is_archived=False) |
            Q(sender=user, is_trashed=True, is_archived=False)).exclude(status='total').order_by('-created_time')
        return render(request, self.template_name, {'trashes': trashes})


class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('categories')


class Reply(LoginRequiredMixin, View):
    template_name = 'mail/reply.html'
    form_class = ReplyForm

    def get(self, request, pk):
        form = self.form_class
        email = Email.objects.get(pk=pk)
        return render(request, self.template_name, {'form': form, 'email': email})

    def post(self, request, pk):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            reply_email = form.save(commit=False)
            sender = Users.objects.get(id=request.user.id)
            reply_email.sender = sender
            reply_email.reply = Email.objects.get(pk=pk)
            receiver = Users.objects.get(id=Email.objects.get(pk=pk).sender_id)
            recipients = Users.objects.get_by_natural_key(username=receiver)
            reply_email.save()
            reply_email.recipients.add(recipients)
            reply_email.is_sent = True
            reply_email.save()
            messages.success(request, 'Email replayed successfully', 'success')
            return redirect('sent')
        messages.error(request, ' Email could not be replayed', 'error')
        logger.error('Email could not be replayed')
        return render(request, self.template_name, {'form': form})


class Forward(LoginRequiredMixin, View):
    template_name = 'mail/forward.html'
    form_class = ForwardForm

    def get(self, request, pk):
        email = Email.objects.get(pk=pk)
        form = self.form_class(instance=email)
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            sender = Users.objects.get(id=request.user.id)
            cd = form.cleaned_data
            to_cc_bcc_list = to_cc_bcc(cd['recipients'], cd['cc'], cd['bcc'])
            # Clear duplicates receiver
            receivers_list = list(dict.fromkeys(to_cc_bcc_list))
            # create one object of email with all recipients,cc,bc and
            # status total to save all data in one object
            total_email = Email.objects.create(sender=sender, subject=cd['subject'],
                                               body=cd['body'], file=cd['file'],
                                               is_sent=True, status='total')
            for receiver in receivers_list:

                if receiver in cd['recipients']:
                    recipients = Users.objects.get_by_natural_key(username=receiver)
                    total_email.recipients.add(recipients)

                elif receiver in cd['cc']:
                    cc_people = Users.objects.get_by_natural_key(username=receiver)
                    total_email.cc.add(cc_people)

                elif receiver in cd['bcc']:
                    bcc_people = Users.objects.get_by_natural_key(username=receiver)
                    total_email.bcc.add(bcc_people)

            total_email.save()

            # create one object email for each receiver
            for receiver in receivers_list:

                if receiver in cd['recipients']:

                    email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                 body=cd['body'], file=cd['file'],
                                                 is_sent=True, status='recipients')

                    recipients = Users.objects.get_by_natural_key(username=receiver)
                    email.recipients.add(recipients)
                    email.save()

                elif receiver in cd['cc']:

                    email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                 body=cd['body'], file=cd['file'],
                                                 is_sent=True, status='cc')

                    recipients = Users.objects.get_by_natural_key(username=receiver)
                    email.recipients.add(recipients)
                    email.save()

                elif receiver in cd['bcc']:

                    email = Email.objects.create(sender=sender, subject=cd['subject'],
                                                 body=cd['body'], file=cd['file'],
                                                 is_sent=True, status='bcc')

                    recipients = Users.objects.get_by_natural_key(username=receiver)
                    email.recipients.add(recipients)
                    email.save()

            messages.success(request, 'Email forwarded successfully', 'success')
            return redirect('home')
        messages.error(request, ' Email could not be forwarded', 'error')
        logger.error(' Email could not be forwarded')
        return render(request, self.template_name, {'form': form})


class Settings(LoginRequiredMixin, View):
    template_name = 'mail/settings.html'

    def get(self, request):
        return render(request, self.template_name, {})


class Filters(LoginRequiredMixin, View):
    template_name = 'mail/filters.html'

    def get(self, request):
        owner = Users.objects.get(id=request.user.id)
        filters = Filter.objects.filter(owner=owner)
        return render(request, self.template_name, {'filters': filters})


class FilterDetail(LoginRequiredMixin, DetailView):
    model = Filter


class CreateFilter(LoginRequiredMixin, View):
    form_class = CreateFilterForm
    template_name = 'mail/create_filter.html'

    def get(self, request):
        form = self.form_class
        labels = Category.objects.filter(owner=request.user)
        return render(request, self.template_name, {'form': form, 'labels': labels})

    def post(self, request):

        form = self.form_class(request.POST)
        user = Users.objects.get(id=request.user.id)
        form.owner = user
        emails = Email.objects.filter(Q(sender=user) | Q(recipients=user) | Q(cc=user) | Q(bcc=user))

        if form.is_valid():

            text = form.cleaned_data['text']
            from_user = form.cleaned_data['from_user']

            # text
            if text:
                for email in emails.filter(Q(body__icontains=text) | Q(subject__icontains=text)):
                    email.is_filter = True

                    if 'Add to Label' in request.POST:
                        label = Category.objects.get(name=request.POST.get('label'), owner=request.user)
                        email.category.add(label)
                        email.save()

                    elif 'Trash' in request.POST:
                        email.is_trashed = True
                        email.save()

                    elif 'Archive' in request.POST:
                        email.is_archived = True
                        email.save()

                # create filter object
                if 'Add to Label' in request.POST:

                    label = Category.objects.get(name=request.POST.get('label'), owner=request.user)
                    Filter.objects.create(owner=user,
                                          text=text,
                                          label=label)
                elif 'Trash' in request.POST:

                    Filter.objects.create(owner=user,
                                          text=text,
                                          trash_or_archive='Trash')

                elif 'Archive' in request.POST:
                    Filter.objects.create(owner=user,
                                          text=text,
                                          trash_or_archive='Archive')
            # from_user
            if from_user:
                for email in emails.filter(sender=user):
                    email.is_filter = True

                    if 'Add to Label' in request.POST:
                        label = Category.objects.get(name=request.POST.get('label'), owner=request.user)
                        email.category.add(label)
                        email.save()

                    elif 'Trash' in request.POST:
                        email.is_trashed = True
                        email.save()

                    elif 'Archive' in request.POST:
                        email.is_archived = True
                        email.save()

                # create filter object
                if 'Add to Label' in request.POST:

                    label = Category.objects.get(name=request.POST.get('label'), owner=request.user)
                    Filter.objects.create(owner=form.owner,
                                          from_user=from_user,
                                          label=label)

                elif 'Trash' in request.POST:

                    Filter.objects.create(owner=form.owner,
                                          from_user=from_user,
                                          trash_or_archive='Trash')

                elif 'Archive' in request.POST:
                    Filter.objects.create(owner=form.owner,
                                          from_user=from_user,
                                          trash_or_archive='Archive')

            messages.success(request, 'Filter created successfully', 'success')
            return redirect('filters')
        messages.error(request, 'Filter not created ', 'error')
        logger.error('Filter not created ')
        return render(request, self.template_name, {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def filter_delete(request, pk):
    filter_obj = Filter.objects.filter(id=pk)
    filter_obj.delete()
    messages.success(request, 'Filter deleted successfully', 'success')
    return redirect('filters')


class SendEmailFromDraft(LoginRequiredMixin, View):

    def get(self, request, pk):
        email_draft = Email.objects.get(pk=pk)
        owner = Users.objects.get(id=request.user.id)
        if email_draft.signature:
            signature = Signature.objects.get(owner=owner, text=email_draft.signature)

        to_cc_bcc_list = to_cc_bcc(email_draft.recipients.all(), email_draft.cc.all(), email_draft.bcc.all())
        # Clear duplicates receiver
        receiver_list = list(dict.fromkeys(to_cc_bcc_list))
        sender = Users.objects.get(id=request.user.id)
        # create one object of email with all recipients,cc,bc and
        # status total to save all data in one object
        total_email = Email.objects.create(sender=sender, subject=email_draft.subject,
                                           body=email_draft.body, file=email_draft.file,
                                           is_sent=True, status='total')
        if email_draft.signature:
            total_email.signature = signature

        for receiver in receiver_list:
            if receiver in email_draft.recipients.all():
                recipients = Users.objects.get_by_natural_key(username=receiver)
                total_email.recipients.add(recipients)

            elif receiver in email_draft.cc.all():
                cc_people = Users.objects.get_by_natural_key(username=receiver)
                total_email.cc.add(cc_people)

            elif receiver in email_draft.bcc.all():
                bcc_people = Users.objects.get_by_natural_key(username=receiver)
                total_email.bcc.add(bcc_people)

        total_email.save()

        # create one object email for each receiver
        for receiver in receiver_list:
            if receiver in email_draft.recipients.all():

                email = Email.objects.create(sender=sender, subject=email_draft.subject,
                                             body=email_draft.body, file=email_draft.file,
                                             is_sent=True, status='recipients')
                if email_draft.signature:
                    email.signature = signature

                recipients = Users.objects.get_by_natural_key(username=receiver)
                email.recipients.add(recipients)
                email.save()

            elif receiver in email_draft.cc.all():

                email = Email.objects.create(sender=sender, subject=email_draft.subject,
                                             body=email_draft.body, file=email_draft.file,
                                             is_sent=True, status='cc')
                if email_draft.signature:
                    email.signature = signature

                recipients = Users.objects.get_by_natural_key(username=receiver)
                email.recipients.add(recipients)
                email.save()

            elif receiver in email_draft.bcc.all():

                email = Email.objects.create(sender=sender, subject=email_draft.subject,
                                             body=email_draft.body, file=email_draft.file,
                                             is_sent=True, status='bcc')
                if email_draft.signature:
                    email.signature = signature

                recipients = Users.objects.get_by_natural_key(username=receiver)
                email.recipients.add(recipients)
                email.save()

        # delete draft email
        email_draft.delete()

        messages.success(request, 'Email sent successfully', 'success')
        return render(request, 'mail/draft.html', {})
