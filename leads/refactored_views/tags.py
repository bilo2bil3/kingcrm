from django.views import generic
from django.urls import reverse_lazy
from leads.models import Tag
from agents.mixins import OrganisorAndLoginRequiredMixin, LoginRequiredMixin


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tag
    fields = ("name",)
    template_name = "leads/add-tag.html"
    success_url = reverse_lazy("leads:add-tag")

    def get_context_data(self, **kwargs):
        kwargs["tags"] = Tag.objects.all()
        return super().get_context_data(**kwargs)


class TagDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Tag
    success_url = reverse_lazy("leads:add-tag")
    template_name = "leads/delete-tag.html"
