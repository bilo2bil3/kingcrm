
from django.urls import path
from .views import (
    LeadListView, LeadDetailView, LeadCreateView, LeadUpdateView, LeadDeleteView,
    AssignAgentView, CategoryListView, CategoryDetailView, LeadCategoryUpdateView,
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView, LeadJsonView, 
    FollowUpCreateView, FollowUpUpdateView, FollowUpDeleteView, upload_leads
)
from . import views

app_name = "leads"

urlpatterns = [
    path('', LeadListView.as_view(), name='lead-list'),
    path('json/', LeadJsonView.as_view(), name='lead-list-json'),
    path('<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),
    path('<int:pk>/update/', LeadUpdateView.as_view(), name='lead-update'),
    path('<int:pk>/delete/', LeadDeleteView.as_view(), name='lead-delete'),
    path('<int:pk>/assign-agent/', AssignAgentView.as_view(), name='assign-agent'),
    path('<int:pk>/category/', LeadCategoryUpdateView.as_view(), name='lead-category-update'),
    path('create/', LeadCreateView.as_view(), name='lead-create'),

    path('<int:pk>/followups/create/', FollowUpCreateView.as_view(), name='lead-followup-create'),
    path('followups/<int:pk>/', FollowUpUpdateView.as_view(), name='lead-followup-update'),
    path('followups/<int:pk>/delete/', FollowUpDeleteView.as_view(), name='lead-followup-delete'),

    path('upload/', upload_leads, name='leads-upload'),
    path('upload/random-agent/', views.upload_leads_with_random_agent, name='leads-upload-random'),
    path('upload/select-agent/', views.upload_leads_with_selected_agent, name='leads-upload-selected'),

    path('search/', views.LeadSearchView.as_view(), name='lead-search'),

    # AJAX URLs
    path('delete-selected-leads', views.delete_selected_leads, name='delete-selected-leads'),
    path('assign-selected-leads', views.assign_selected_leads, name='assign-selected-leads'),

    # path('export-leads', views.export_leads, name='export-leads'),

    # c2c
    path('click2call', views.click_to_call, name='click2call'),
    path('click2call-hangup', views.hangup_call, name='click2call-hangup'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('create-category/', CategoryCreateView.as_view(), name='category-create'),
]