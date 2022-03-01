from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views import View
from django.contrib import messages
from .models import Users, Email
from mail.forms import CreateMailForm, EmailModelForm
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView


# Create your views here.
class EmailCreateView(BSModalCreateView):
    template_name = 'mail/create_email.html'
    form_class = EmailModelForm
    success_message = 'Success: Email was created.'
    success_url = reverse_lazy('index')


class CreateMail(View):
    form_class = CreateMailForm
    template_name = 'mail/create_new_mail.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            sender = request.user
            new_mail = Email.objects.create(sender=sender,
                                            body=form.cleaned_data['body'],
                                            subject=form.cleaned_data['subject'],
                                            file=form.cleaned_data['file'],
                                            )
            new_mail.save(commit=False)
            new_mail.is_sent = True
            new_mail.save()
            messages.success(request, 'mail sent successfully')
            return redirect('/')
