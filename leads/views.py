import logging
import datetime
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import generic
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Agent
from .forms import (
    CustomUserCreationForm,
    AssignAgentForm,
    LeadCategoryUpdateForm,
)
import csv

from .utils import add_query_string

logger = logging.getLogger(__name__)


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
    #     #     lead_before_update = self.get_object()
    #     #     instance = form.save(commit=False)
    #     #     converted_category = Category.objects.get(name="Converted")
    #     #     if form.cleaned_data["category"] == converted_category:
    #     #         # update the date at which this lead was converted
    #     #         if lead_before_update.category != converted_category:
    #     #             # this lead has now been converted
    #     #             instance.converted_date = datetime.datetime.now()
    #     #     instance.save()
    #     #     return super(LeadCategoryUpdateView, self).form_valid(form)
    #     pass
