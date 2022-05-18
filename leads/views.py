import logging
import datetime
from django import contrib
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q, Count, ExpressionWrapper, IntegerField
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse_lazy
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent, Category, FollowUp, LeadsSheet, Tag
from .forms import (
    LeadForm,
    LeadModelForm,
    CustomUserCreationForm,
    AssignAgentForm,
    LeadCategoryUpdateForm,
    CategoryModelForm,
    FollowUpModelForm,
    UploadLeadsForm,
    UploadLeadsWithAgentForm,
    SearchLeadsForm,
    LeadsSheetForm,
)
from . import forms
from csv import DictReader
import io
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl, parse_qs
import json
import csv
import requests
from . import stats
from . import exporter

logger = logging.getLogger(__name__)


import environ

env = environ.Env()
READ_DOT_ENV_FILE = env.bool("READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    environ.Env.read_env()


# CRUD+L - Create, Retrieve, Update and Delete + List


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard_form")
        return super().dispatch(request, *args, **kwargs)


def landing_page(request):
    return render(request, "landing.html")


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    paginate_by = 7

    # override default get method
    # to handle both cases of:
    # generate leads csv or view leads
    def get(self, request, *args, **kwargs):
        if "export=1" in request.get_full_path():
            response = HttpResponse(
                content_type="text/csv",
            )
            response[
                "Content-Disposition"
            ] = 'attachment; filename="exported-leads.csv"'
            writer = csv.writer(response)
            qs = self.get_queryset()
            writer.writerow(
                [
                    "FIRST NAME",
                    "LAST NAME",
                    "SOURCE",
                    "SERVICE",
                    "EMAIL",
                    "CELL PHONE NUMBER",
                    "COUNTRY",
                    "CAMPAIGN",
                    "AGENT",
                    "CATEGORY",
                    "DATE",
                ]
            )
            for lead in qs:
                writer.writerow(
                    [
                        lead.first_name,
                        lead.last_name,
                        lead.source,
                        lead.service,
                        lead.email,
                        lead.phone_number,
                        lead.country,
                        lead.campaign,
                        (
                            f"{lead.agent.user.first_name} {lead.agent.user.last_name}"
                            if lead.agent
                            else "Unassigned"
                        ),
                        (lead.category.name if lead.category else "New"),
                        lead.date_added.date(),
                    ]
                )
            return response
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                # agent__isnull=False
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
                # agent__isnull=False
            )
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)

        # print('###', self.request.GET)
        # if self.request.GET.get('first_name'):
        if (
            "?" in self.request.get_full_path()
            and "first_name" in self.request.get_full_path()
        ):
            first_name = self.request.GET["first_name"]
            last_name = self.request.GET["last_name"]
            email = self.request.GET["email"]
            phone_number = self.request.GET["phone_number"]
            first_name_q = Q(first_name__icontains=first_name)
            last_name_q = Q(last_name__icontains=last_name)
            email_q = Q(email__startswith=email)
            phone_number_q = Q(phone_number__icontains=phone_number)

            sources = self.request.GET.getlist("source")
            services = self.request.GET.getlist("service")
            countries = self.request.GET.getlist("country")
            campaigns = self.request.GET.getlist("campaign")
            agents = self.request.GET.getlist("agent")
            categories = self.request.GET.getlist("category")
            tags = self.request.GET.getlist("tag")
            # charfields fileters
            # either membership filter (to include selected only)
            # or starts with empty str filter (to include all)
            if not sources:
                sources_q = Q(source__startswith="")
            else:
                sources_q = Q(source__in=sources)
            if not services:
                services_q = Q(service__startswith="")
            else:
                services_q = Q(service__in=services)
            if not countries:
                countries_q = Q(country__startswith="")
            else:
                countries_q = Q(country__in=countries)
            if not campaigns:
                campaigns_q = Q(campaign__startswith="")
            else:
                campaigns_q = Q(campaign__in=campaigns)

            queryset = queryset.filter(
                first_name_q
                & last_name_q
                & email_q
                & phone_number_q
                & sources_q
                & services_q
                & countries_q
                & campaigns_q
            )
            # fks filters
            # only membership filter
            if agents:
                queryset = queryset.filter(agent__pk__in=agents)
            if categories:
                queryset = queryset.filter(category__pk__in=categories)
            if tags:
                queryset = queryset.filter(tags__in=tags)

            # datetime filters
            # either in specific range
            # or from specific date till today
            start_date = self.request.GET["start_date"]
            end_date = self.request.GET["end_date"]
            if start_date and end_date:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                queryset = queryset.filter(
                    date_added__gte=start_date, date_added__lte=end_date
                )
            elif start_date:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                queryset = queryset.filter(date_added__date=start_date)

        # sorting
        ordering = self.request.GET.get("order_by", None)
        if ordering is None:
            # add default ordering
            ordering = "-date_added"
        if ordering == "country_desc":
            ordering = "-country"
        elif ordering == "country_asc":
            ordering = "country"
        elif ordering == "campaign_desc":
            ordering = "-campaign"
        elif ordering == "campaign_asc":
            ordering = "campaign"
        elif ordering == "agent_desc":
            ordering = "-agent__user__first_name"
        elif ordering == "agent_asc":
            ordering = "agent__user__first_name"
        elif ordering == "category_desc":
            ordering = "-category__name"
        elif ordering == "category_asc":
            ordering = "category__name"
        elif ordering == "date_desc":
            ordering = "-date_added"
        elif ordering == "date_asc":
            ordering = "date_added"
        return queryset.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        # control sorting flags
        url = self.request.get_full_path()
        for field in ["country", "campaign", "agent", "category", "date"]:
            params1 = {f"order_by": f"{field}_asc"}
            params2 = {f"order_by": f"{field}_desc"}
            url_asc = add_query_string(url, params1)
            url_desc = add_query_string(url, params2)
            context.update({f"{field}_url_asc": url_asc, f"{field}_url_desc": url_desc})

        # add pagination links
        page_obj = context["page_obj"]
        if page_obj.has_previous():
            first_page = add_query_string(url, {"page": 1})
            previous_page = add_query_string(
                url, {"page": page_obj.previous_page_number()}
            )
            context.update(
                {"first_page_url": first_page, "previous_page_url": previous_page}
            )
        if page_obj.has_next():
            next_page = add_query_string(url, {"page": page_obj.next_page_number()})
            last_page = add_query_string(url, {"page": page_obj.paginator.num_pages})
            context.update({"next_page_url": next_page, "last_page_url": last_page})
        ten_pages = []
        for i in range(
            max(1, page_obj.number - 5),
            min(page_obj.number + 5, page_obj.paginator.num_pages) + 1,
        ):
            ten_pages.append({i: add_query_string(url, {"page": i})})
        context.update({"ten_pages": ten_pages})

        # add export link
        export_link = add_query_string(url, {"export": 1})
        context.update({"export_link": export_link})

        # to assign leads from lead_list view
        # we need show all agents
        context.update({"agents": Agent.objects.all()})
        # user = self.request.user
        # if user.is_organisor:
        #     queryset = Lead.objects.filter(
        #         organisation=user.userprofile,
        #         agent__isnull=True
        #     )
        #     context.update({
        #         "unassigned_leads": queryset
        #     })
        return context


def lead_list(request):
    leads = Lead.objects.all()
    context = {"leads": leads}
    return render(request, "leads/lead_list.html", context)


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {"lead": lead}
    return render(request, "leads/lead_detail.html", context)


class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"],
        )
        messages.success(self.request, "You have successfully created a lead")
        return super(LeadCreateView, self).form_valid(form)


def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {"form": form}
    return render(request, "leads/lead_create.html", context)


class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        form.save()
        messages.info(self.request, "You have successfully updated this lead")
        return super(LeadUpdateView, self).form_valid(form)


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {"form": form, "lead": lead}
    return render(request, "leads/lead_update.html", context)


class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"

    def get_success_url(self):
        return reverse("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)

        context.update(
            {"unassigned_lead_count": queryset.filter(category__isnull=True).count()}
        )
        return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class CategoryCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def form_valid(self, form):
        category = form.save(commit=False)
        category.organisation = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class CategoryDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/category_delete.html"

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})

    # def form_valid(self, form):
    #     lead_before_update = self.get_object()
    #     instance = form.save(commit=False)
    #     converted_category = Category.objects.get(name="Converted")
    #     if form.cleaned_data["category"] == converted_category:
    #         # update the date at which this lead was converted
    #         if lead_before_update.category != converted_category:
    #             # this lead has now been converted
    #             instance.converted_date = datetime.datetime.now()
    #     instance.save()
    #     return super(LeadCategoryUpdateView, self).form_valid(form)


class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/followup_create.html"
    form_class = FollowUpModelForm

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super(FollowUpCreateView, self).get_context_data(**kwargs)
        context.update({"lead": Lead.objects.get(pk=self.kwargs["pk"])})
        return context

    def form_valid(self, form):
        lead = Lead.objects.get(pk=self.kwargs["pk"])
        followup = form.save(commit=False)
        followup.lead = lead
        followup.save()
        return super(FollowUpCreateView, self).form_valid(form)


class FollowUpUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/followup_update.html"
    form_class = FollowUpModelForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = FollowUp.objects.filter(lead__organisation=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(
                lead__organisation=user.agent.organisation
            )
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().lead.id})


class FollowUpDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/followup_delete.html"

    def get_success_url(self):
        followup = FollowUp.objects.get(id=self.kwargs["pk"])
        return reverse("leads:lead-detail", kwargs={"pk": followup.lead.pk})

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = FollowUp.objects.filter(lead__organisation=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(
                lead__organisation=user.agent.organisation
            )
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset


# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()
#             return redirect("/leads")
# context = {
#     "form": form,
#     "lead": lead
# }
#     return render(request, "leads/lead_update.html", context)


# def lead_create(request):
# form = LeadForm()
# if request.method == "POST":
#     form = LeadForm(request.POST)
#     if form.is_valid():
#         first_name = form.cleaned_data['first_name']
#         last_name = form.cleaned_data['last_name']
#         age = form.cleaned_data['age']
#         agent = Agent.objects.first()
#         Lead.objects.create(
#             first_name=first_name,
#             last_name=last_name,
#             age=age,
#             agent=agent
#         )
#         return redirect("/leads")
# context = {
#     "form": form
# }
#     return render(request, "leads/lead_create.html", context)


class LeadJsonView(generic.View):
    def get(self, request, *args, **kwargs):

        qs = list(Lead.objects.all().values("first_name", "last_name", "age"))

        return JsonResponse(
            {
                "qs": qs,
            }
        )


### upload leads using csv file ###
def partition_leads(leads, agents_count):
    """split leads evenly between agents"""
    # to do so
    # we need to slice leads into N equal groups
    # where N is number of agents
    k, m = divmod(len(leads), agents_count)
    return [
        leads[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
        for i in range(agents_count)
    ]


def add_leads_and_assign_random_agent(request, f):
    f = io.StringIO(f.read().decode("utf-8"))
    csv_reader = DictReader(f)

    # to skip duplicate leads while uploading
    # we need to keep track of leads added for current session
    leads_to_add = []
    for row in csv_reader:
        print(row)
        if row["phone_number"] in [lead["phone_number"] for lead in leads_to_add]:
            continue
        leads_to_add.append(row)

    agents = Agent.objects.all()
    agents_count = Agent.objects.count()

    parts = partition_leads(leads_to_add, agents_count)

    for i, agent in enumerate(agents):
        leads_per_agent = parts[i]
        for lead in leads_per_agent:
            first_name = lead["first_name"]
            last_name = lead["last_name"]
            source = lead["source"]
            service = lead["service"]
            email = lead["email"]
            phone_number = lead["phone_number"]
            country = lead["country"]
            campaign = lead["campaign"]

            # skip duplicate leads
            # if new lead exist in db
            if phone_number in Lead.objects.values_list("phone_number", flat=True):
                continue

            Lead.objects.create(
                organisation=request.user.userprofile,
                first_name=first_name,
                last_name=last_name,
                source=source,
                service=service,
                email=email,
                phone_number=phone_number,
                country=country,
                campaign=campaign,
                agent=agent,
            )


def add_leads_and_assign_selected_agent(request, f, agent):
    f = io.StringIO(f.read().decode("utf-8"))
    csv_reader = DictReader(f)

    # to skip duplicate leads while uploading
    # we need to keep track of leads added for current session
    leads_to_add = []
    for row in csv_reader:
        if row["phone_number"] in [lead["phone_number"] for lead in leads_to_add]:
            continue
        leads_to_add.append(row)

    for lead in leads_to_add:
        first_name = lead["first_name"]
        last_name = lead["last_name"]
        source = lead["source"]
        service = lead["service"]
        email = lead["email"]
        phone_number = lead["phone_number"]
        country = lead["country"]
        campaign = lead["campaign"]

        # skip duplicate leads
        # if new lead exist in db
        if phone_number in Lead.objects.values_list("phone_number", flat=True):
            continue

        Lead.objects.create(
            organisation=request.user.userprofile,
            first_name=first_name,
            last_name=last_name,
            source=source,
            service=service,
            email=email,
            phone_number=phone_number,
            country=country,
            campaign=campaign,
            agent=agent,
        )


def add_leads(request, f):
    f = io.StringIO(f.read().decode("utf-8"))
    csv_reader = DictReader(f)

    # to skip duplicate leads while uploading
    # we need to keep track of leads added for current session
    leads_to_add = []
    for row in csv_reader:
        if row["phone_number"] in [lead["phone_number"] for lead in leads_to_add]:
            continue
        leads_to_add.append(row)

    for lead in leads_to_add:
        first_name = lead["first_name"]
        last_name = lead["last_name"]
        source = lead["source"]
        service = lead["service"]
        email = lead["email"]
        phone_number = lead["phone_number"]
        country = lead["country"]
        campaign = lead["campaign"]

        # skip duplicate leads
        # if new lead exist in db
        if phone_number in Lead.objects.values_list("phone_number", flat=True):
            continue

        Lead.objects.create(
            organisation=request.user.userprofile,
            first_name=first_name,
            last_name=last_name,
            source=source,
            service=service,
            email=email,
            phone_number=phone_number,
            country=country,
            campaign=campaign,
        )


def upload_leads(request):
    if request.method == "POST":
        form = UploadLeadsForm(request.POST, request.FILES)
        if form.is_valid():
            add_leads(request, request.FILES["leads_file"])
            return redirect(reverse("leads:lead-list"))
    else:
        form = UploadLeadsForm()
    return render(request, "leads/leads_upload.html", {"form": form})


def upload_leads_with_random_agent(request):
    if request.method == "POST":
        form = UploadLeadsForm(request.POST, request.FILES)
        if form.is_valid():
            add_leads_and_assign_random_agent(request, request.FILES["leads_file"])
            return redirect(reverse("leads:lead-list"))
    else:
        form = UploadLeadsForm()
    return render(request, "leads/leads_upload_random.html", {"form": form})


def upload_leads_with_selected_agent(request):
    if request.method == "POST":
        form = UploadLeadsWithAgentForm(request.POST, request.FILES)
        if form.is_valid():
            add_leads_and_assign_selected_agent(
                request, request.FILES["leads_file"], form.cleaned_data["agent"]
            )
            return redirect(reverse("leads:lead-list"))
    else:
        form = UploadLeadsWithAgentForm()
    return render(request, "leads/leads_upload_selected.html", {"form": form})


### search leads ###
class LeadSearchView(generic.edit.FormView):
    template_name = "leads/lead_search.html"
    form_class = SearchLeadsForm
    # success_url = reverse_lazy('leads:lead-list')


def add_query_string(url, params):
    url_parts = list(urlparse(url))
    query = dict(parse_qs(url_parts[4], keep_blank_values=True))
    query.update(params)
    qs_parts = []
    for k, v in query.items():
        if isinstance(v, (str, int)):
            qs_parts.append((k, v))
        elif isinstance(v, list):
            for f in v:
                qs_parts.append((k, f))
    url_parts[4] = urlencode(qs_parts)
    return urlunparse(url_parts)


@login_required
def delete_selected_leads(request):
    if request.method == "POST":
        # print('####handling delete selected leads')
        payload = json.loads(request.body)
        url = payload["url"]
        # print('###current url', url)
        leads_to_delete = list(map(int, payload["leads"]))
        # print('###', leads_to_delete)
        qs = Lead.objects.filter(pk__in=leads_to_delete)
        # print('###', qs)
        qs.delete()
        return HttpResponseRedirect(url)


@login_required
def assign_selected_leads(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        url = payload["url"]
        agent_ids = payload["agents"]
        leads_to_assign = list(map(int, payload["leads"]))

        # qs = Lead.objects.filter(pk__in=leads_to_assign)
        # qs.update(agent=agent_id)

        agents = Agent.objects.filter(pk__in=agent_ids)
        agents_count = len(agents)
        parts = partition_leads(leads_to_assign, agents_count)
        for i, agent in enumerate(agents):
            leads_per_agent = parts[i]
            for lead_id in leads_per_agent:
                Lead.objects.filter(pk=lead_id).update(agent=agent)
        return HttpResponseRedirect(url)


@login_required
def assign_selected_leads_randomly(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        url = payload["url"]
        leads_to_assign = list(map(int, payload["leads"]))

        agents = Agent.objects.all()
        agents_count = Agent.objects.count()
        parts = partition_leads(leads_to_assign, agents_count)
        for i, agent in enumerate(agents):
            leads_per_agent = parts[i]
            for lead_id in leads_per_agent:
                Lead.objects.filter(pk=lead_id).update(agent=agent)
        return HttpResponseRedirect(url)


@login_required
def click_to_call(request):
    if request.method == "POST":
        CALL_ENDPOINT = env("CLICK2CALL_CALL_ENDPOINT")
        AGENT_NUMBER = env("CLICK2CALL_AGENT_NUMBER")
        payload = json.loads(request.body)
        lead_id = payload["lead"]
        lead = Lead.objects.get(pk=lead_id)
        client_number = lead.phone_number
        print(f"###click2call: calling {client_number}")
        try:
            r = requests.post(
                CALL_ENDPOINT, data={"agent": AGENT_NUMBER, "phone_num": client_number}
            )
            lead.last_called = datetime.datetime.now()
            lead.save()
            return HttpResponse("")
        except Exception as e:
            return HttpResponse(str(e))


@login_required
def hangup_call(request):
    if request.method == "POST":
        print("###click2call: disconneting")
        HANGUP_ENDPOINT = env("CLICK2CALL_HANGUP_ENDPOINT")
        AGENT_NUMBER = env("CLICK2CALL_AGENT_NUMBER")
        try:
            r = requests.post(HANGUP_ENDPOINT, data={"agent": AGENT_NUMBER})
            return HttpResponse("")
        except Exception as e:
            return HttpResponse(str(e))


class SheetCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    form_class = LeadsSheetForm
    template_name = "leads/add-sheet.html"
    # success_url = reverse_lazy('leads:lead-list')
    success_url = reverse_lazy("leads:add-sheet")

    def form_valid(self, form):
        form.instance.organisation = self.request.user.userprofile
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs["sheets"] = LeadsSheet.objects.all()
        return super().get_context_data(**kwargs)


class SheetDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    model = LeadsSheet
    success_url = reverse_lazy("leads:add-sheet")
    template_name = "leads/delete-sheet.html"


class TagCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    model = Tag
    fields = ("name",)
    template_name = "leads/add-tag.html"
    success_url = reverse_lazy("leads:add-tag")

    def get_context_data(self, **kwargs):
        kwargs["tags"] = Tag.objects.all()
        return super().get_context_data(**kwargs)


class TagDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    model = Tag
    success_url = reverse_lazy("leads:add-tag")
    template_name = "leads/delete-tag.html"


class StatsListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name: str = "leads/stats_list.html"

    def get_queryset(self):
        """get all agents whose ids match filtered ids -from stats form-."""
        agents_ids = self.request.GET.getlist("agent")
        queryset = Agent.objects.filter(pk__in=agents_ids)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_dates()
        agents = self.get_queryset()
        data = []
        for agent in agents:
            data.append(stats.calculate_stats(start_date, end_date, agent))
        print("start date", str(start_date.date()))
        print("end date", str(end_date.date()))
        context.update(
            {
                "data": data,
                "start_date": str(start_date.date()),
                "end_date": str(end_date.date()),
            }
        )

        export_link = add_query_string(self.request.get_full_path(), {"export": 1})
        context.update({"export_link": export_link})

        return context

    def get(self, request, *args, **kwargs):
        """a custom handler for http get that can handle both cases of:
        - show stats at a webpage
        - export stats as a csv file
        """
        if "export=1" in request.get_full_path():
            start_date, end_date = self.get_dates()
            agents = self.get_queryset()
            rows = []
            for agent in agents:
                row = {
                    "start date": str(start_date.date()),
                    "end date": str(end_date.date()),
                }
                agent_stats = stats.calculate_stats(start_date, end_date, agent)
                row.update(agent_stats)
                rows.append(row)
            header = row.keys()
            # TODO: howto format header? (eg. make all fields uppercase)
            # header = [k.upper() for k in row.keys()]
            return exporter.export_csv(header, rows, "stats_export.csv")
        return super().get(request, *args, **kwargs)

    def get_dates(self):
        """return start and end dates as date objects not strings.
        so they're suitable for calculating agents stats."""
        # get dates from query string
        start_date = self.request.GET["start_date"]
        end_date = self.request.GET["end_date"]
        # cast them to date objects
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            # should add 1 day period to end_date so it reaches midnight
            end_date = datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            )  # + datetime.timedelta(days=1)
        elif start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date  # + datetime.timedelta(days=1)
        return start_date, end_date


class StatsFilterView(OrganisorAndLoginRequiredMixin, generic.FormView):
    form_class = forms.StatsFilterForm
    template_name = "leads/stats_filter.html"


class DashboardFormView(OrganisorAndLoginRequiredMixin, generic.FormView):
    """display a form to select a start and end dates
    that are used to calculate some stats
    for DashboardListView.
    """

    form_class = forms.DashboardForm
    template_name = "leads/dashboard_form.html"


class DashboardListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    """display/export stats for each catg, total leads
    and converted leads during a specific period."""

    template_name = "leads/dashboard_list.html"
    model = Lead

    def get_context_data(self, **kwargs):
        context = {}
        start_date, end_date = self.get_dates()
        # TODO: how do these fields affect queried leads?
        # organisation, user.userprofile...
        # user = self.request.user
        # total_lead_count = Lead.objects.filter(organisation=user.userprofile).count()
        total_lead_count = Lead.objects.filter(
            date_added__date__gte=start_date,
            date_added__date__lte=end_date,
        ).count()
        catgs = Category.objects.filter(
            leads__date_added__date__gte=start_date,
            leads__date_added__date__lte=end_date,
        ).annotate(
            percentage=ExpressionWrapper(
                Count("leads") * 100.0 / total_lead_count,
                output_field=IntegerField(),
            )
        )
        unassigned_lead_count = int(
            Lead.objects.filter(category__isnull=True).count() / total_lead_count * 100
        )
        converted_lead_count = catgs.get(name="Converted").leads.count()
        export_link = add_query_string(self.request.get_full_path(), {"export": 1})
        context.update(
            {
                "total_lead_count": total_lead_count,
                "converted_lead_count": converted_lead_count,
                "start_date": str(start_date.date()),
                "end_date": str(end_date.date()),
                "catgs": catgs,
                "unassigned_lead_count": unassigned_lead_count,
                "export_link": export_link,
            }
        )
        return context

    def get_dates(self):
        """return start and end dates as date objects not strings.
        so they're suitable for calculating agents stats."""
        # get dates from query string
        start_date = self.request.GET["start_date"]
        end_date = self.request.GET["end_date"]
        # cast them to date objects
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            # TODO: do i need to add 1 day period
            # to end_date so it reaches midnight?
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        elif start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date
        return start_date, end_date

    def get(self, request, *args, **kwargs):
        """a custom handler for http get that can handle both cases of:
        - show stats at a webpage
        - export stats as a csv file
        """
        if "export=1" in request.get_full_path():
            context = self.get_context_data()
            del context["export_link"]
            catgs = context.pop("catgs")
            for catg in catgs:
                context[catg.name] = f"{catg.percentage}%"
            rows = [context]
            header = context.keys()
            filename = "dashboard_export.csv"
            return exporter.export_csv(header, rows, filename)
        return super().get(request, *args, **kwargs)
