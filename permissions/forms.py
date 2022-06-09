from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from permissions.models import Permission


class PermissionModelForm(forms.ModelForm):
    name = forms.CharField()
    code = forms.CharField()
    # confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Permission
        fields = (
            "name",
            "code",
        )

    # def clean(self):
    #     cleaned_data = super(PermissionModelForm, self).clean()
    #     code = cleaned_data.get("code")
    #     name = cleaned_data.get("name")
        
        # if Permission.objects.filter(name__iexact=name, code__iexact=code).exists():
        #     raise forms.ValidationError("This permission already exists")
