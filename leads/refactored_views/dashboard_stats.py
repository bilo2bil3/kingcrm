import datetime
from django.views import generic
from django.db.models import ExpressionWrapper, Count, IntegerField, Q, F
from agents.mixins import LoginRequiredMixin, OrganisorAndLoginRequiredMixin
from leads import exporter
from leads.forms import DashboardForm
from leads.models import Lead, Category
from leads.utils import add_query_string


class DashboardFormView(LoginRequiredMixin, generic.FormView):
    """display a form to select a start and end dates
    that are used to calculate some stats
    for DashboardListView.
    """

    form_class = DashboardForm
    template_name = "leads/dashboard_form.html"


class DashboardListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    """display/export stats for each catg, total leads
    and converted leads during a specific period."""

    template_name = "leads/dashboard_list.html"
    model = Lead

    def get_context_data(self, **kwargs):
        context = {}
        start_date, end_date = self.get_dates()
        # print("###start_date", start_date)
        # print("###end_date", end_date)

        total_lead_count = Lead.objects.filter(
            date_added__date__gte=start_date,
            date_added__date__lte=end_date,
        ).count()
        # print("###total_lead_count", total_lead_count)

        # TODO: handle ZeroDivisionError when there are no leads yet!
        catgs = (
            Category.objects.all()
            .annotate(
                leads_count_in_period=Count(
                    "leads",
                    filter=(
                        Q(leads__date_added__date__gte=start_date)
                        & Q(leads__date_added__date__lte=end_date)
                    ),
                )
            )
            .annotate(
                percentage=ExpressionWrapper(
                    F("leads_count_in_period") * 100.0 / total_lead_count,
                    output_field=IntegerField(),
                )
            )
        )
        # print("###catgs", catgs)

        unassigned_lead_count = int(
            Lead.objects.filter(category__isnull=True).count() / total_lead_count * 100
        )

        converted_lead_count = catgs.get(name="Converted").leads.count()

        export_link = add_query_string(self.request.get_full_path(), {"export": 1})

        context.update(
            {
                "total_lead_count": total_lead_count,
                "converted_lead_count": converted_lead_count,
                "start_date": str(start_date.date()),
                "end_date": str(end_date.date()),
                "catgs": catgs,
                "unassigned_lead_count": unassigned_lead_count,
                "export_link": export_link,
            }
        )
        return context

    def get_dates(self):
        """return start and end dates as date objects not strings.
        so they're suitable for calculating agents stats."""
        # get dates from query string
        start_date = self.request.GET["start_date"]
        end_date = self.request.GET["end_date"]
        # cast them to date objects
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            # TODO: do i need to add 1 day period
            # to end_date so it reaches midnight?
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        elif start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date
        return start_date, end_date

    def get(self, request, *args, **kwargs):
        """a custom handler for http get that can handle both cases of:
        - show stats at a webpage
        - export stats as a csv file
        """
        if "export=1" in request.get_full_path():
            context = self.get_context_data()
            del context["export_link"]
            catgs = context.pop("catgs")
            for catg in catgs:
                context[catg.name] = f"{catg.percentage}%"
            rows = [context]
            header = context.keys()
            filename = "dashboard_export.csv"
            return exporter.export_csv(header, rows, filename)
        return super().get(request, *args, **kwargs)
