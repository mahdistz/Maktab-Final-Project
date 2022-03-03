from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from .models import Users, Email, Category
from mail.forms import CreateMailForm, CreateContactForm, CreateCategoryForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
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
            email = Email.objects.create(sender=user,
                                         body=form.cleaned_data['body'],
                                         subject=form.cleaned_data['subject'],
                                         file=form.cleaned_data['file'],
                                         )
            recipients_list = list(form.cleaned_data['recipients'])
            cc_list = list(form.cleaned_data['cc'])
            bcc_list = list(form.cleaned_data['bcc'])
            for people in recipients_list:
                email.recipients.add(people)
                email.save()
            if cc_list:
                for people in cc_list:
                    email.cc.add(people)
                    email.save()
            elif bcc_list:
                for people in bcc_list:
                    email.bcc.add(people)
                    email.save()
            email.save()
        messages.success(request, 'mail sent successfully')
        return redirect('home')


class ContactList(ListView):
    model = Contact


class CreateContact(View):
    form_class = CreateContactForm
    template_name = 'user/create_contact.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
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


class EmailList(ListView):
    model = Email


class EmailDetail(DetailView):
    model = Email

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_read'] = True
        return context


class EmailDelete(DeleteView):
    model = Email
    success_url = reverse_lazy('emails')


class ContactDelete(DeleteView):
    model = Contact
    success_url = reverse_lazy('contacts')


class CategoryDelete(DeleteView):
    model = Category
    success_url = reverse_lazy('categories')


class ContactUpdate(UpdateView):
    model = Contact
    template_name = 'user/contact_update.html'
    fields = ['name', 'birth_date1', 'other_email', 'phone_number1']
    success_url = reverse_lazy('contacts')
