from django.shortcuts import render
from django.shortcuts import reverse
from django.views import generic
from agents.mixins import OrganisorAndLoginRequiredMixin, LoginRequiredMixin
from permissions.forms import PermissionModelForm
from .models import Permission

class PermissionListView(LoginRequiredMixin, generic.ListView):
    template_name = "permission_list.html"
    
    def get_queryset(self):
        return Permission.objects.all()
    
class PermissionCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "permission_create.html"
    form_class = PermissionModelForm

    def get_success_url(self):
        return reverse("permissions:permission-list")

    def form_valid(self, form):        
        return super(PermissionCreateView, self).form_valid(form)

class PermissionUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "permission_update.html"
    form_class = PermissionModelForm

    def get_success_url(self):
        return reverse("permissions:permission-list")

    def get_queryset(self):
        return Permission.objects.all()


class PermissionDeleteView(LoginRequiredMixin, generic.DeleteView):
    template_name = "permission_delete.html"
    context_object_name = "permission"

    def get_success_url(self):
        return reverse("permissions:permission-list")

    def get_queryset(self):
        return Permission.objects.all()
