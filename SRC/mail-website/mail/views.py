from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from .models import Email, Category
from user.models import Users
from mail.forms import CreateMailForm, CreateCategoryForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin


class CreateMail(LoginRequiredMixin, View):
    form_class = CreateMailForm
    template_name = 'mail/create_new_mail.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

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

            elif form.cleaned_data['bcc']:
                for people in form.cleaned_data['bcc']:
                    bcc_receiver = Users.objects.get_by_natural_key(username=people)
                    email.bcc.add(bcc_receiver)

            email.save()
        messages.success(request, 'mail sent successfully')
        return redirect('home')


class CategoryList(LoginRequiredMixin, ListView):
    model = Category


class CategoryDetail(LoginRequiredMixin, DetailView):
    model = Category


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


class EmailDelete(LoginRequiredMixin, DeleteView):
    model = Email
    success_url = reverse_lazy('emails')


class CategoryDelete(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('categories')
