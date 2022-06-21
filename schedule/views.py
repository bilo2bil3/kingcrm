from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.views import generic
from agents.mixins import LoginRequiredMixin
from leads.models import FollowUp, Lead
from schedule.forms import ScheduleModelForm
from .models import Schedule
from channels.layers import get_channel_layer

# Create your views here.
class ScheduleListView(LoginRequiredMixin, generic.ListView):
    template_name = "schedule_list.html"
    
    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user)
    
class ScheduleCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "schedule_create.html"
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("schedule:schedule-list")

    def form_valid(self, form):
        return super(ScheduleCreateView, self).form_valid(form)
    
    def post(self, request, *args, **kwargs):
        data = request.POST
        lead = Lead.objects.get(pk=data['lead'])
        reminder = Schedule(lead=lead, title=data['title'], date=data['date'], time=data['time'], user=request.user)
        reminder.save()
        return HttpResponseRedirect(self.get_success_url())

class ScheduleUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "schedule_update.html"
    form_class = ScheduleModelForm

    def get_success_url(self):
        return reverse("schedule:schedule-list")

    def get_queryset(self):
        return Schedule.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.POST
        lead = Lead.objects.get(pk=data['lead'])
        
        reminder = Schedule.objects.get(pk=kwargs['pk'])
        reminder.lead = lead
        reminder.title = data['title']
        reminder.date = data['date']
        reminder.time = data['time']
        reminder.save()
        
        return HttpResponseRedirect(self.get_success_url())

class ScheduleDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "schedule_delete.html"
    context_object_name = "schedule"

    def get_success_url(self):
        return reverse("schedule:schedule-list")

    def get_queryset(self):
        return Schedule.objects.all()

from asgiref.sync import async_to_sync
def test(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notification_reminder',{
            'type': 'send_notification',
            'message': 'Notification'
        }
    )
    
    return HttpResponse("Done")