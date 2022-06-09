import random

from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from leads.models import Agent
from permissions.models import Permission
from .forms import AgentModelForm
from .mixins import OrganisorAndLoginRequiredMixin
from django.shortcuts import render


class AgentListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)

class AgentPermissionListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name = "permissions/agent_permission_list.html"
    
    def get_queryset(self):
        self.context = {
           "permissions": Permission.objects.all(),
           "agent": Agent.objects.get(pk=self.kwargs['pk'])
        }
        return self.context
    
    def get_success_url(self):
        return reverse("agents:agent-list")

    def post(self, request, *args, **kwargs):
        permission_codes = request.POST.getlist('permissions')
        
        permissions = []
        
        agent = Agent.objects.get(pk=kwargs['pk'])
        
        agent.permissions.clear()
        
        for code in permission_codes:
            temp = Permission.objects.get(code=code)
            permissions.append(temp)
            agent.permissions.add(temp)
            
        agent.save()
    
        return HttpResponseRedirect(self.get_success_url())


class AgentCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organisor = False
        user.set_password(user.password)
        user.save()
        Agent.objects.create(
            user=user,
            organisation=self.request.user.userprofile
        )
        # send_mail(
        #     subject="You are invited to be an agent",
        #     message="You were added as an agent on DJCRM. Please come login to start working.",
        #     from_email="admin@test.com",
        #     recipient_list=[user.email]
        # )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrganisorAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent"

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)


class AgentUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)

class AgentDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent"

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)
