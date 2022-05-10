from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import Lead, Agent, Category, FollowUp, LeadsSheet, Tag

User = get_user_model()


class LeadModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tags field
        # should only appear when updating an existing lead
        # not when creating a new lead
        if self.instance.pk is not None:
            self.fields['remove tags'] = forms.MultipleChoiceField(choices=self.get_existing_tags(), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
            self.fields['add tags'] = forms.MultipleChoiceField(choices=self.get_new_tags(), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))

    class Meta:
        model = Lead
        fields = (
            'first_name',
            'last_name',
            'source',
            'service',
            'agent',
            'description',
            'phone_number',
            'country',
            'campaign',
            'email',
            'profile_picture'
        )

    def clean_first_name(self):
        data = self.cleaned_data["first_name"]
        # if data != "Joe":
        #     raise ValidationError("Your name is not Joe")
        return data

    def clean(self):
        pass
        # first_name = self.cleaned_data["first_name"]
        # last_name = self.cleaned_data["last_name"]
        # if first_name + last_name != "Joe Soap":
        #     raise ValidationError("Your name is not Joe Soap")

    def get_existing_tags(self):
        return [('', '------')] + [(tag.pk, tag) for tag in self.instance.tags.all()]

    def get_new_tags(self):
        return [('', '------')] + [(tag.pk, tag) for tag in Tag.objects.exclude(leads__pk=self.instance.pk)]

    def save(self, *args, **kwargs):
        try:
            tags_to_add = self.cleaned_data.pop('add tags')
            tags_to_remove = self.cleaned_data.pop('remove tags')
        except KeyError:
            pass
        else:
            for tag_id in tags_to_add:
                self.instance.tags.add(tag_id)
            for tag_id in tags_to_remove:
                self.instance.tags.remove(tag_id)
        return super().save(*args, **kwargs)


class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    source = forms.CharField()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}


class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organisation=request.user.userprofile)
        super(AssignAgentForm, self).__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            'category',
        )


class CategoryModelForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = (
            'name',
        )


class FollowUpModelForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = (
            'notes',
            'file'
        )


class UploadLeadsForm(forms.Form):
    # TODO: how to enable accept attribute?
    # by default wont work
    # so you can create a custom widget instead?
    # leads_file = forms.FileField(accept="text/csv")
    leads_file = forms.FileField()


class UploadLeadsWithAgentForm(forms.Form):
    leads_file = forms.FileField()
    agent = forms.ModelChoiceField(queryset=Agent.objects.all())


class DateInput(forms.DateInput):
    input_type = 'date'


### search leads ###
class SearchLeadsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source'] = forms.MultipleChoiceField(choices=self.get_choices('source'), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
        self.fields['service'] = forms.MultipleChoiceField(choices=self.get_choices('service'), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
        self.fields['country'] = forms.MultipleChoiceField(choices=self.get_choices('country'), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
        self.fields['agent'] = forms.MultipleChoiceField(choices=self.get_agents(), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
        self.fields['campaign'] = forms.MultipleChoiceField(choices=self.get_choices('campaign'), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
        self.fields['category'] = forms.MultipleChoiceField(choices=self.get_catgs(), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))
        self.fields['tag'] = forms.MultipleChoiceField(choices=self.get_tags(), required=False, widget=forms.SelectMultiple(attrs={'multiple': 'multiple'}))

    # text input
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone_number = forms.CharField(required=False)
    start_date = forms.DateField(required=False, widget=DateInput())
    end_date = forms.DateField(required=False, widget=DateInput())
    # select input
    # must be dynamic (ie. reflect db state)
    # so should be included in __init__ method instead

    def get_choices(self, field_name):
        return [('', '------')] + [(v,v) for v in Lead.objects.values_list(field_name, flat=True).distinct()]

    def get_agents(self):
        return [
            ('', '------')] + [(agent.pk, f'{agent.user.first_name} {agent.user.last_name}')
            for agent in Agent.objects.all()
        ]

    def get_catgs(self):
        return [('', '------')] + [(catg.pk, catg) for catg in Category.objects.all()]

    def get_tags(self):
        return [('', '------')] + [(tag.pk, tag) for tag in Tag.objects.all()]

### load from google sheets ###
class LeadsSheetForm(forms.ModelForm):
    class Meta:
        model = LeadsSheet
        fields = ('source', 'url', 'sheet_name')
