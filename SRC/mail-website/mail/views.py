from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect, Http404
from django.views import View
from django.contrib import messages
from .models import Email, Category
from user.models import Users
from mail.forms import CreateMailForm, CreateCategoryForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError


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
                                         signature=form.cleaned_data['signature'],
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


class AllEmailOfCategory(LoginRequiredMixin, View):
    template_name = 'mail/all_email_of_category.html'

    def get(self, request):
        emails_of_category = Email.category.all()
        return render(request, self.template_name, {'emails_of_category': emails_of_category})


class CreateCategory(LoginRequiredMixin, View):
    form_class = CreateCategoryForm
    template_name = 'mail/create_category.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'category created successfully', 'success')
        return render(request, self.template_name, {'form': form})


class EmailList(LoginRequiredMixin, ListView):
    model = Email


class EmailDetail(LoginRequiredMixin, DetailView):
    model = Email


class InboxMail(LoginRequiredMixin, View):
    def get(self, request):
        recipients = Email.objects.filter(recipients=request.user.id)
        cc = Email.objects.filter(cc=request.user.id)
        bcc = Email.objects.filter(bcc=request.user.id)

        return render(request, 'mail/inbox.html',
                      {'recipients': recipients, 'cc': cc, 'bcc': bcc})


class DraftMail(LoginRequiredMixin, View):
    def get(self, request):
        drafts = Email.objects.filter(sender=request.user.id).filter(is_sent=False)
        return render(request, 'mail/draft.html', {'drafts': drafts})


class ArchiveMail(LoginRequiredMixin, View):
    def get(self, request):
        archives = Email.objects.filter(is_archived=True)
        return render(request, 'mail/archive.html', {'archives': archives})


class TrashMail(LoginRequiredMixin, View):
    def get(self, request):
        trashes = Email.objects.filter(is_trashed=True)
        return render(request, 'mail/trash.html', {'trashes': trashes})


class EmailDelete(LoginRequiredMixin, DeleteView):
    model = Email
    success_url = reverse_lazy('emails')


class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('categories')
