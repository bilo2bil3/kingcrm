import datetime
from django.views import generic
from agents.mixins import OrganisorAndLoginRequiredMixin, LoginRequiredMixin
from leads import stats, exporter
from leads.forms import StatsFilterForm
from leads.models import Agent
from leads.utils import add_query_string


class StatsFilterView(LoginRequiredMixin, generic.FormView):
    form_class = StatsFilterForm
    template_name = "leads/stats_filter.html"


class StatsListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/stats_list.html"

    def get_queryset(self):
        """get all agents whose ids match filtered ids -from stats form-."""
        agents_ids = self.request.GET.getlist("agent")
        queryset = Agent.objects.filter(pk__in=agents_ids)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_dates()
        agents = self.get_queryset()
        data = []
        for agent in agents:
            data.append(stats.calculate_stats(start_date, end_date, agent))
        # print("start date", str(start_date.date()))
        # print("end date", str(end_date.date()))
        context.update(
            {
                "data": data,
                "start_date": str(start_date.date()),
                "end_date": str(end_date.date()),
            }
        )

        export_link = add_query_string(self.request.get_full_path(), {"export": 1})
        context.update({"export_link": export_link})

        return context

    def get(self, request, *args, **kwargs):
        """a custom handler for http get that can handle both cases of:
        - show stats at a webpage
        - export stats as a csv file
        """
        if "export=1" in request.get_full_path():
            start_date, end_date = self.get_dates()
            agents = self.get_queryset()
            rows = []
            for agent in agents:
                row = {
                    "start date": str(start_date.date()),
                    "end date": str(end_date.date()),
                }
                agent_stats = stats.calculate_stats(start_date, end_date, agent)
                row.update(agent_stats)
                rows.append(row)
            header = row.keys()
            # TODO: howto format header? (eg. make all fields uppercase)
            # header = [k.upper() for k in row.keys()]
            return exporter.export_csv(header, rows, "stats_export.csv")
        return super().get(request, *args, **kwargs)

    def get_dates(self):
        """return start and end dates as date objects not strings.
        so they're suitable for calculating agents stats."""
        # get dates from query string
        start_date = self.request.GET["start_date"]
        end_date = self.request.GET["end_date"]
        # cast them to date objects
        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            # should add 1 day period to end_date so it reaches midnight
            end_date = datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            )  # + datetime.timedelta(days=1)
        elif start_date:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date = start_date  # + datetime.timedelta(days=1)
        return start_date, end_date
