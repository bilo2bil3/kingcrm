from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

from leads.models import Agent


class LoginRequiredMixin(AccessMixin):
    
    """Verify that the current user is authenticated and is an organisor."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("leads:lead-list")
        return super().dispatch(request, *args, **kwargs)

class OrganisorAndLoginRequiredMixin(AccessMixin):
    
    """Verify that the current user is authenticated and is an organisor."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_organisor:
            return redirect("leads:lead-list")
        return super().dispatch(request, *args, **kwargs)

class PermissionAndLoginRequiredMixin(AccessMixin):
    def get_page_code(self):
        return
    
    def dispatch(self, request, *args, **kwargs):
        agent = None
        try:
            agent = Agent.objects.get(user=request.user)
        except Agent.DoesNotExist:
            pass
        if not request.user.is_authenticated or (agent and not agent.permissions.filter(code=self.get_page_code()).exists()):
            return redirect("leads:lead-list")
        return super().dispatch(request, *args, **kwargs)