from django.urls import path
from .views import (
    LeadListView,
    AssignAgentView,
    LeadCategoryUpdateView,
)
from .refactored_views import (
    sales_report,
    agent_stats,
    tags,
    sheets,
    click2call,
    upload,
    catgs,
    ajax,
    followups,
    search,
    leads_views,
)

app_name = "leads"

urlpatterns = [
    path("", LeadListView.as_view(), name="lead-list"),
    path("json/", leads_views.LeadJsonView.as_view(), name="lead-list-json"),
    path("<int:pk>/", leads_views.LeadDetailView.as_view(), name="lead-detail"),
    path("<int:pk>/update/", leads_views.LeadUpdateView.as_view(), name="lead-update"),
    path("<int:pk>/delete/", leads_views.LeadDeleteView.as_view(), name="lead-delete"),
    path("<int:pk>/assign-agent/", AssignAgentView.as_view(), name="assign-agent"),
    path(
        "<int:pk>/category/",
        LeadCategoryUpdateView.as_view(),
        name="lead-category-update",
    ),
    path("create/", leads_views.LeadCreateView.as_view(), name="lead-create"),
    # followups
    path(
        "<int:pk>/followups/create/",
        followups.FollowUpCreateView.as_view(),
        name="lead-followup-create",
    ),
    path(
        "followups/<int:pk>/",
        followups.FollowUpUpdateView.as_view(),
        name="lead-followup-update",
    ),
    path(
        "followups/<int:pk>/delete/",
        followups.FollowUpDeleteView.as_view(),
        name="lead-followup-delete",
    ),
    # uplaod leads from csv
    path("upload/", upload.upload_leads, name="leads-upload"),
    path(
        "upload/random-agent/",
        upload.upload_leads_with_random_agent,
        name="leads-upload-random",
    ),
    path(
        "upload/select-agent/",
        upload.upload_leads_with_selected_agent,
        name="leads-upload-selected",
    ),
    path("search/", search.LeadSearchView.as_view(), name="lead-search"),
    # AJAX URLs
    path(
        "delete-selected-leads",
        ajax.delete_selected_leads,
        name="delete-selected-leads",
    ),
    path(
        "assign-selected-leads",
        ajax.assign_selected_leads,
        name="assign-selected-leads",
    ),
    path(
        "assign-selected-leads-randomly",
        ajax.assign_selected_leads_randomly,
        name="assign-selected-leads-randomly",
    ),
    # path('export-leads', views.export_leads, name='export-leads'),
    # c2c
    path("click2call", click2call.click_to_call, name="click2call"),
    path("click2call-hangup", click2call.hangup_call, name="click2call-hangup"),
    # google sheets
    path("add-sheet", sheets.SheetCreateView.as_view(), name="add-sheet"),
    path(
        "sheets/<int:pk>/delete", sheets.SheetDeleteView.as_view(), name="delete-sheet"
    ),
    # tags
    path("add-tag/", tags.TagCreateView.as_view(), name="add-tag"),
    path("tags/<int:pk>/delete/", tags.TagDeleteView.as_view(), name="delete-tag"),
    # agent stats
    path("stats/", agent_stats.StatsListView.as_view(), name="stats_list"),
    path("stats/filter", agent_stats.StatsFilterView.as_view(), name="stats_filter"),
    # catgs
    path("categories/", catgs.CategoryListView.as_view(), name="category-list"),
    path(
        "categories/<int:pk>/",
        catgs.CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "categories/<int:pk>/update/",
        catgs.CategoryUpdateView.as_view(),
        name="category-update",
    ),
    path(
        "categories/<int:pk>/delete/",
        catgs.CategoryDeleteView.as_view(),
        name="category-delete",
    ),
    path(
        "create-category/", catgs.CategoryCreateView.as_view(), name="category-create"
    ),
    # sales report
    path(
        "sales_report/new/",
        sales_report.SalesReportCreateView.as_view(),
        name="sales-report-new",
    ),
    path(
        "sales_report/",
        sales_report.SalesReportListView.as_view(),
        name="sales-report-list",
    ),
    path(
        "sales_report/<int:pk>/",
        sales_report.SalesReportDetailView.as_view(),
        name="sales-report-detail",
    ),
]
