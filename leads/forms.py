from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import Lead, Agent, Category, FollowUp, LeadsSheet, Tag
from .custom_form_fields import (
    DateField,
    ModelMultiSelectField,
    ModelAttributeMultiSelectField,
)
from . import models

User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            "first_name",
            "last_name",
            "source",
            "service",
            "agent",
            # "description",
            "phone_number",
            "country",
            "campaign",
            "email",
            # "profile_picture",
        )

    def clean_first_name(self):
        data = self.cleaned_data["first_name"]
        # if data != "Joe":
        #     raise ValidationError("Your name is not Joe")
        return data

    def clean(self):
        # first_name = self.cleaned_data["first_name"]
        # last_name = self.cleaned_data["last_name"]
        # if first_name + last_name != "Joe Soap":
        #     raise ValidationError("Your name is not Joe Soap")
        pass


class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    source = forms.CharField()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}


class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organisation=request.user.userprofile)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadCategoryUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tags field
        # should only appear when updating an existing lead
        # not when creating a new lead
        self.fields["remove tags"] = forms.MultipleChoiceField(
            choices=self.get_existing_tags(),
            required=False,
            widget=forms.SelectMultiple(attrs={"multiple": "multiple"}),
        )
        self.fields["add tags"] = forms.MultipleChoiceField(
            choices=self.get_new_tags(),
            required=False,
            widget=forms.SelectMultiple(attrs={"multiple": "multiple"}),
        )

    class Meta:
        model = Lead
        fields = ("category",)

    def get_existing_tags(self):
        return [("", "------")] + [(tag.pk, tag) for tag in self.instance.tags.all()]

    def get_new_tags(self):
        return [("", "------")] + [
            (tag.pk, tag) for tag in Tag.objects.exclude(leads__pk=self.instance.pk)
        ]

    def save(self, *args, **kwargs):
        try:
            tags_to_add = self.cleaned_data.pop("add tags")
            tags_to_remove = self.cleaned_data.pop("remove tags")
        except KeyError:
            pass
        else:
            for tag_id in tags_to_add:
                self.instance.tags.add(tag_id)
            for tag_id in tags_to_remove:
                self.instance.tags.remove(tag_id)
        return super().save(*args, **kwargs)


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)


class FollowUpModelForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ("notes", "file")


class UploadLeadsForm(forms.Form):
    # TODO: how to enable accept attribute?
    # by default wont work
    # so you can create a custom widget instead?
    # leads_file = forms.FileField(accept="text/csv")
    leads_file = forms.FileField()


class UploadLeadsWithAgentForm(forms.Form):
    leads_file = forms.FileField()
    agent = forms.ModelChoiceField(queryset=Agent.objects.all())


### search leads ###
class SearchLeadsForm(forms.Form):
    # text input
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False)
    start_date = DateField(required=False)
    end_date = DateField(required=False)
    # select input
    agent = ModelMultiSelectField(queryset=Agent.objects.all(), required=False)
    category = ModelMultiSelectField(queryset=Category.objects.all(), required=False)
    source = ModelAttributeMultiSelectField("source", required=False)
    service = ModelAttributeMultiSelectField("service", required=False)
    country = ModelAttributeMultiSelectField("country", required=False)
    campaign = ModelAttributeMultiSelectField("campaign", required=False)
    tag = ModelMultiSelectField(queryset=Tag.objects.all(), required=False)



### agent stats/reports ###
class StatsFilterForm(forms.Form):
    """
    to show agent stats during a specific period,
    we need a form to select the agent, a start and an end date.
    """

    start_date = DateField(required=True)
    end_date = DateField(required=False)
    agent = ModelMultiSelectField(queryset=Agent.objects.all())


### dashboard ###
class DashboardForm(forms.Form):
    """
    to show crm stats during a specific period,
    we need a form to select a start and an end date.
    """

    start_date = DateField(required=True)
    end_date = DateField(required=True)


class SalesReportForm(forms.ModelForm):
    class Meta:
        model = models.SalesReport
        fields = (
            "agent",
            "year",
            "month",
            "performance",
            "kpi_rate",
            "revenu",
            "best_service",
            "customer_support",
        )
