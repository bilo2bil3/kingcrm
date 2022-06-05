"""views called from javascript."""
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from leads.models import Lead, Agent
from .upload import partition_leads


@login_required
def delete_selected_leads(request):
    if request.method == "POST":
        payload = json.loads(request.body)
        url = payload["url"]
        leads_to_delete = list(map(int, payload["leads"]))
        qs = Lead.objects.filter(pk__in=leads_to_delete)
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
