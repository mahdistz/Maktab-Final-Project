from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from .models import Users, Email, Category
from mail.forms import CreateMailForm, CreateContactForm, CreateCategoryForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from user.models import Contact


class CreateMail(View):
    form_class = CreateMailForm
    template_name = 'mail/create_new_mail.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = Users.objects.get(id=request.user.id)
            print(user)
            email = Email(sender=user,
                          body=form.cleaned_data['body'],
                          subject=form.cleaned_data['subject'],
                          file=form.cleaned_data['file'],
                          )
            recipients = list(form.cleaned_data['recipients'])
            cc = list(form.cleaned_data['cc'])
            bcc = list(form.cleaned_data['bcc'])
            for people in recipients:
                email.recipients.add(people)
                email.save()
            if cc:
                for people in cc:
                    email.cc.add(people)
                    email.save()
            elif bcc:
                for people in bcc:
                    email.bcc.add(people)
                    email.save()
            form.save()
        messages.success(request, 'mail sent successfully')
        return redirect('home')


class ContactList(ListView):
    model = Contact


class CreateContact(View):
    form_class = CreateContactForm
    template_name = 'user/create_contact.html'

    def get(self, request):
        form = self.form_class
        user = Users.objects.get(id=request.user.id)
        return render(request, self.template_name, {'form': form, 'user': user})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'contact created successfully', 'success')
        return render(request, self.template_name, {'form': form})


class ContactDetail(DetailView):
    model = Contact


class CategoryList(ListView):
    model = Category


class CategoryDetail(DetailView):
    model = Category


class CreateCategory(View):
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
