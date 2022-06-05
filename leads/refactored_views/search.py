from django.views import generic
from leads.forms import SearchLeadsForm


class LeadSearchView(generic.edit.FormView):
    template_name = "leads/lead_search.html"
    form_class = SearchLeadsForm
    # success_url = reverse_lazy('leads:lead-list')
