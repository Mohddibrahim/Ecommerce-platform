from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control rounded-3"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control rounded-3"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control rounded-3"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control rounded-3"
        })