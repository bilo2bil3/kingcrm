from django import forms
from .models import Lead


### custom widgets ###
class DateInput(forms.DateInput):
    input_type = "date"


class SelectMultiple(forms.SelectMultiple):
    # TODO: why must add multiple attrb here?
    # because of tailwind code
    # where html attribute "multiple"
    # doesn't have effect / doesn't appear
    # for some reason
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs = {"multiple": "multiple"}


### custom fields ###
class DateField(forms.DateField):
    widget = DateInput


class ModelMultiSelectField(forms.ModelChoiceField):
    widget = SelectMultiple


# TODO: why can't use this one instead of above
# check reason above (@SelectMultiple)
class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = SelectMultiple


class ModelAttributeMultiSelectField(forms.MultipleChoiceField):
    widget = SelectMultiple

    def __init__(self, field_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = self.get_choices(field_name)

    def get_choices(self, field_name):
        return [("", "------")] + [
            (v, v) for v in Lead.objects.values_list(field_name, flat=True).distinct()
        ]
