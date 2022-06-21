from django import forms
from .models import Schedule
from leads.custom_form_fields import (
    DateField,
    TimeField,
)


class ScheduleModelForm(forms.ModelForm):
    date = DateField()
    time = TimeField()

    class Meta:
        model = Schedule
        fields = (
            "lead",
            "title",
            "date",
            "time",
        )