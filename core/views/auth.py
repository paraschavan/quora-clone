from django.views.generic import CreateView
from django.urls import reverse_lazy
from core.forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html' 