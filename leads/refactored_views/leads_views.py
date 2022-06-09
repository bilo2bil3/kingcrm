from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from agents.mixins import OrganisorAndLoginRequiredMixin, PermissionAndLoginRequiredMixin
from leads.models import Lead
from leads.forms import LeadModelForm


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


class LeadCreateView(PermissionAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm
    
    def get_page_code(self):
        return 'create'

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        # TODO: is this required?
        # send_mail(
        #     subject="A lead has been created",
        #     message="Go to the site to see the new lead",
        #     from_email="test@test.com",
        #     recipient_list=["test2@test.com"],
        # )
        # messages.success(self.request, "You have successfully created a lead")
        return super().form_valid(form)


class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm
    success_url = reverse_lazy("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)

    def form_valid(self, form):
        form.save()
        # messages.info(self.request, "You have successfully updated this lead")
        return super().form_valid(form)


class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    success_url = reverse_lazy("leads:lead-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        return Lead.objects.filter(organisation=user.userprofile)


class LeadJsonView(generic.View):
    def get(self, request, *args, **kwargs):
        qs = list(Lead.objects.all().values("first_name", "last_name", "age"))
        return JsonResponse({"qs": qs})


# TODO: are these views still used/required?
# i think CBV are doing work atm
def lead_list(request):
    leads = Lead.objects.all()
    context = {"leads": leads}
    return render(request, "leads/lead_list.html", context)


def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {"lead": lead}
    return render(request, "leads/lead_detail.html", context)


def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {"form": form}
    return render(request, "leads/lead_create.html", context)


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {"form": form, "lead": lead}
    return render(request, "leads/lead_update.html", context)


# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             age = form.cleaned_data['age']
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()
#             return redirect("/leads")
# context = {
#     "form": form,
#     "lead": lead
# }
#     return render(request, "leads/lead_update.html", context)

# def lead_create(request):
# form = LeadForm()
# if request.method == "POST":
#     form = LeadForm(request.POST)
#     if form.is_valid():
#         first_name = form.cleaned_data['first_name']
#         last_name = form.cleaned_data['last_name']
#         age = form.cleaned_data['age']
#         agent = Agent.objects.first()
#         Lead.objects.create(
#             first_name=first_name,
#             last_name=last_name,
#             age=age,
#             agent=agent
#         )
#         return redirect("/leads")
# context = {
#     "form": form
# }
#     return render(request, "leads/lead_create.html", context)
