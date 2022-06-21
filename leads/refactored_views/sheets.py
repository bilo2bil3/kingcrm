from django.views import generic
from django.urls import reverse_lazy
from leads.forms import LeadsSheetForm
from leads.models import LeadsSheet
from agents.mixins import OrganisorAndLoginRequiredMixin, LoginRequiredMixin


class SheetCreateView(LoginRequiredMixin, generic.CreateView):
    # model = LeadsSheet
    # fields = ("source", "url", "sheet_name")
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


class SheetDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = LeadsSheet
    success_url = reverse_lazy("leads:add-sheet")
    template_name = "leads/delete-sheet.html"
