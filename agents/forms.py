from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from leads.models import Agent

User = get_user_model()


class AgentModelForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "click2call_extension",
        )

    def clean(self):
        cleaned_data = super(AgentModelForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password and confirm_password does not match")

# class AgentPermissionModelForm(forms.ModelForm):
#     class Meta:
#         model = Agent
#         fields = (
#             "permissions",
#         )

    # def clean(self):
    #     cleaned_data = super(AgentModelForm, self).clean()
    #     password = cleaned_data.get("password")
    #     confirm_password = cleaned_data.get("confirm_password")

    #     if password != confirm_password:
    #         raise forms.ValidationError("password and confirm_password does not match")
