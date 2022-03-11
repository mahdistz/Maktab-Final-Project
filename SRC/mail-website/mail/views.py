from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect, Http404
from django.views import View
from django.contrib import messages
from user.forms import SearchContactForm
from .models import Email, Category
from user.models import Users
from mail.forms import CreateMailForm, CreateCategoryForm, AddEmailToCategoryForm, ForwardForm, ReplyForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q


class CreateMail(LoginRequiredMixin, View):
    form_class = CreateMailForm

    def get(self, request):
        form = self.form_class
        return render(request, 'home.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = Users.objects.get(id=request.user.id)
            email = Email.objects.create(sender=user,
                                         body=form.cleaned_data['body'],
                                         subject=form.cleaned_data['subject'],
                                         file=form.cleaned_data['file'],
                                         )
            for people in form.cleaned_data['recipients']:
                recipients = Users.objects.get_by_natural_key(username=people)
                email.recipients.add(recipients)

            if form.cleaned_data['cc']:
                for people in form.cleaned_data['cc']:
                    cc_receiver = Users.objects.get_by_natural_key(username=people)
                    email.cc.add(cc_receiver)

            if form.cleaned_data['bcc']:
                for people in form.cleaned_data['bcc']:
                    bcc_receiver = Users.objects.get_by_natural_key(username=people)
                    email.bcc.add(bcc_receiver)

            if 'save' in request.POST:
                # When the user presses the save button, email's field is_sent=True,
                # then email object saved.
                email.is_sent = True
                email.save()
                messages.success(request, 'mail sent successfully', 'success')

            if 'cancel' in request.POST:
                # When the user presses the cancel button, email's field is_sent=False (by default),
                # and email object saved. save with is_sent = False to show email on Draft
                email.save()
                messages.info(request, 'mail saved in draft', 'info')
            return render(request, 'home.html', {})

        else:
            messages.error(request, "mail doesn't sent,error occurred (file size should not exceed 25 MB)", 'error')
            return render(request, 'home.html', {})


class CategoryList(LoginRequiredMixin, ListView):
    model = Category


class CategoryDetail(LoginRequiredMixin, DetailView):
    model = Category


class CategoriesOfEmail(LoginRequiredMixin, View):
    template_name = 'mail/categories.html'

    def get(self, request):
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        owner = Category.objects.filter(owner=user)
        categories = owner.categories.all()
        return render(request, self.template_name, {'categories': categories})


class AllEmailOfCategory(LoginRequiredMixin, View):
    template_name = 'mail/all_email_of_category.html'

    def get(self, request, pk):
        category = Category.objects.get(pk=pk)
        emails = Email.objects.filter(category__owner=request.user, category__exact=category)
        return render(request, self.template_name, {'emails': emails})


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
            category.save()
            messages.success(request, 'category created successfully', 'success')
            return redirect('categories')
        return render(request, self.template_name, {'form': form})


class AddEmailToCategory(LoginRequiredMixin, View):
    form_class = AddEmailToCategoryForm
    template_name = 'mail/add_email_to_category.html'

    def get(self, request, pk):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, pk):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = Email.objects.get(pk=pk)
            category_obj = Category.objects.get(name=form.cleaned_data['name'])
            email.category.add(category_obj)
            email.save()
            messages.success(request, 'email added to the label successfully', 'success')
            return redirect('categories')
        return render(request, self.template_name, {'form': form})


class EmailList(LoginRequiredMixin, ListView):
    model = Email


class EmailDetail(LoginRequiredMixin, DetailView):
    model = Email


class InboxMail(LoginRequiredMixin, View):
    template_name = 'mail/inbox.html'

    def get(self, request):
        emails = Email.objects.filter(Q(recipients=request.user.id) | Q(cc=request.user.id) | Q(bcc=request.user.id)).\
            order_by('-created_time')
        return render(request, self.template_name, {'emails': emails})


class SentMail(LoginRequiredMixin, View):
    template_name = 'mail/sent.html'

    def get(self, request):
        sent = Email.objects.filter(sender__exact=request.user.id)

        return render(request, self.template_name,
                      {'sent': sent})


class DraftMail(LoginRequiredMixin, View):
    template_name = 'mail/draft.html'

    def get(self, request):
        drafts = Email.objects.filter(sender=request.user.id).filter(is_sent=False)
        return render(request, self.template_name, {'drafts': drafts})


# class ArchiveMail(LoginRequiredMixin, View):
#     template_name = 'mail/archive.html'
#
#     def get(self, request, pk):
#         email_of_user = UpdateEmailOfUser.objects.get(user=request.user, email_id__in=pk)
#         email_of_user.is_archived = True
#         email_of_user.save()
#         archives = UpdateEmailOfUser.objects.filter(user=request.user, is_archived=True)
#         return render(request, self.template_name, {'archives': archives})
#
#
# class TrashMail(LoginRequiredMixin, View):
#     template_name = 'mail/trash.html'
#
#     def get(self, request, pk):
#         email_of_user = UpdateEmailOfUser.objects.get(user=request.user, email_id__in=pk)
#         email_of_user.is_trashed = True
#         email_of_user.save()
#         trashes = UpdateEmailOfUser.objects.filter(user=request.user, is_trashed=True)
#         return render(request, self.template_name, {'trashes': trashes})


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
            reply_email.reply_to = Email.objects.get(pk=pk)
            receiver = Users.objects.get(id=Email.objects.get(pk=pk).sender_id)
            recipients = Users.objects.get_by_natural_key(username=receiver)
            reply_email.save()
            reply_email.recipients.add(recipients)
            reply_email.is_sent = True
            reply_email.save()
            messages.success(request, 'mail sent successfully', 'success')
            return redirect('home')
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
            forward = Email.objects.create(sender=sender,
                                           subject=form.cleaned_data['subject'],
                                           body=form.cleaned_data['body'],
                                           file=form.cleaned_data['file'],
                                           )

            for people in form.cleaned_data['recipients']:
                recipients = Users.objects.get_by_natural_key(username=people)
                forward.recipients.add(recipients)

            if form.cleaned_data['cc']:
                for people in form.cleaned_data['cc']:
                    cc_receiver = Users.objects.get_by_natural_key(username=people)
                    forward.cc.add(cc_receiver)

            if form.cleaned_data['bcc']:
                for people in form.cleaned_data['bcc']:
                    bcc_receiver = Users.objects.get_by_natural_key(username=people)
                    forward.bcc.add(bcc_receiver)

            forward.is_sent = True
            forward.save()
            messages.success(request, 'mail sent successfully', 'success')
            return redirect('home')
        return render(request, self.template_name, {'form': form})
