import io
from csv import DictReader
from django.shortcuts import render, redirect
from django.urls import reverse
from leads.models import Agent, Lead
from leads.forms import UploadLeadsForm, UploadLeadsWithAgentForm


def filter_duplicate_rows(csv_reader):
    """
    return a list of leads to add
    where duplicate leads (by phone number) have been removed.
    """
    leads_to_add = []
    for row in csv_reader:
        # print(row)
        if row["phone_number"] in [lead["phone_number"] for lead in leads_to_add]:
            continue
        leads_to_add.append(row)
    return leads_to_add


def populate_db(leads_to_add, organisation, agent=None):
    """add leads to db."""
    for lead in leads_to_add:
        # skip lead if already exists in db
        if lead["phone_number"] in Lead.objects.values_list("phone_number", flat=True):
            continue

        fields = {
            "organisation": organisation,
            "first_name": lead["first_name"],
            "last_name": lead["last_name"],
            "source": lead["source"],
            "service": lead["service"],
            "email": lead["email"],
            "phone_number": lead["phone_number"],
            "country": lead["country"],
            "campaign": lead["campaign"],
        }
        if agent is not None:
            fields["agent"] = agent

        Lead.objects.create(**fields)


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


def add_leads(request, f, agent=None, assign_randomly=False):
    """
    read leads from uploaded csv file and add them to db.
    if agent is None: leads will be unassigned
    if agent is None and assign_randomly is True:
        leads will be evenly distributed between
        agents that are currently in db
    if agent is not None: leads will be assigned to that agent
    """
    f = io.StringIO(f.read().decode("utf-8"))
    csv_reader = DictReader(f)
    leads_to_add = filter_duplicate_rows(csv_reader)
    if agent is None and assign_randomly:
        agents, agents_count = Agent.objects.all(), Agent.objects.count()
        parts = partition_leads(leads_to_add, agents_count)
        for i, agent in enumerate(agents):
            leads_per_agent = parts[i]
            populate_db(leads_per_agent, request.user.userprofile, agent)
        return
    populate_db(leads_to_add, request.user.userprofile, agent)


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
            add_leads(
                request, request.FILES["leads_file"], agent=None, assign_randomly=True
            )
            return redirect(reverse("leads:lead-list"))
    else:
        form = UploadLeadsForm()
    return render(request, "leads/leads_upload_random.html", {"form": form})


def upload_leads_with_selected_agent(request):
    if request.method == "POST":
        form = UploadLeadsWithAgentForm(request.POST, request.FILES)
        if form.is_valid():
            add_leads(request, request.FILES["leads_file"], form.cleaned_data["agent"])
            return redirect(reverse("leads:lead-list"))
    else:
        form = UploadLeadsWithAgentForm()
    return render(request, "leads/leads_upload_selected.html", {"form": form})
