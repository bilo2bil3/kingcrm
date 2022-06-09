from django.urls import path
from .views import PermissionCreateView, PermissionDeleteView, PermissionListView, PermissionUpdateView

app_name = 'permissions'

urlpatterns = [
    path('', PermissionListView.as_view(), name='permission-list'), 
    path('create/', PermissionCreateView.as_view(), name='permission-create'),
    path('<int:pk>/update/', PermissionUpdateView.as_view(), name='permission-update'),
    path('<int:pk>/delete/', PermissionDeleteView.as_view(), name='permission-delete'),
]