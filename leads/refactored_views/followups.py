from datetime import datetime, time
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.urls import reverse
from agents.mixins import OrganisorAndLoginRequiredMixin
from leads.models import Lead, FollowUp
from leads.forms import FollowUpModelForm
from schedule.models import ReminderNotification, Schedule


class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/followup_create.html"
    form_class = FollowUpModelForm

    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"lead": Lead.objects.get(pk=self.kwargs["pk"])})
        return context

    def form_valid(self, form):
        form.instance.lead = Lead.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        data = request.POST
        
        if data.get('is_reminder') == 'true':
            lead = Lead.objects.get(pk=kwargs['pk'])
            schedule = Schedule.objects.create(lead=lead, title=data['title'], date=data['date'], time=data['time'])
            notification = ReminderNotification.objects.create(
                user=request.user,
                lead=lead,
                message=data.get('title'),
                reminder_on=datetime.combine(datetime.strptime(schedule.date, '%Y-%m-%d'), datetime.strptime(schedule.time, '%H:%M').time())
            )
            schedule.save()
            notification.save()
        
        return super().post(request, *args, **kwargs)

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


class FollowUpDeleteView(LoginRequiredMixin, generic.DeleteView):
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
