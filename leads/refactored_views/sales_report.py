from django.views import generic
from django.urls import reverse_lazy
from agents.mixins import OrganisorAndLoginRequiredMixin, LoginRequiredMixin
from leads.forms import SalesReportForm
from leads.models import SalesReport


class SalesReportCreateView(LoginRequiredMixin, generic.FormView):
    """display a form to select an agent, a year, a month and some questions
    that are used to evaluate agent performance.
    """

    template_name = "leads/salesreport_new.html"
    form_class = SalesReportForm
    success_url = reverse_lazy("leads:sales-report-list")

    def form_valid(self, form):
        total_rate = int(
            (
                int(form.cleaned_data["performance"])
                + int(form.cleaned_data["kpi_rate"])
                + int(form.cleaned_data["revenu"])
                + int(form.cleaned_data["best_service"])
                + int(form.cleaned_data["customer_support"])
            )
            / 500
            * 100
        )
        form.instance.total_rate = str(total_rate)
        form.save()
        return super().form_valid(form)


class SalesReportListView(LoginRequiredMixin, generic.ListView):
    model = SalesReport
    context_object_name = "reports"
    template_name = "leads/salesreport_list.html"


class SalesReportDetailView(LoginRequiredMixin, generic.DetailView):
    model = SalesReport
    context_object_name = "report"
    template_name = "leads/salesreport_detail.html"
