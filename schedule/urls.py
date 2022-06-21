from django.urls import path
from .views import ScheduleCreateView, ScheduleDeleteView, ScheduleListView, ScheduleUpdateView, test

app_name = 'schedule'

urlpatterns = [
    path('', ScheduleListView.as_view(), name='schedule-list'), 
    path('create/', ScheduleCreateView.as_view(), name='schedule-create'),
    path('test/', test),
    # path('<int:pk>/leads/create/', ScheduleCreateView.as_view(), name='lead-reminder-create'),
    path('<int:pk>/update/', ScheduleUpdateView.as_view(), name='schedule-update'),
    path('<int:pk>/delete/', ScheduleDeleteView.as_view(), name='schedule-delete'),
]