from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
# Create your views here.
from mail.forms import CreateMailForm


class CreateMail(View):
    form_class = CreateMailForm
    template_name = 'mail/create_new_mail.html'

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            messages.success(request, 'mail sent successfully')
            return redirect('/')
