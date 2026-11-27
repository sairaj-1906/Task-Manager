from django.urls import path
from .api import TaskCollectionAPI, TaskDetailAPI
from . import views

urlpatterns = [
    path("api/tasks/", TaskCollectionAPI.as_view(), name="api_task_list"),
    path("api/tasks/<int:pk>/", TaskDetailAPI.as_view(), name="api_task_detail"),
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    path("tasks/new/", views.TaskCreateView.as_view(), name="task_create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="task_update"),
    path("tasks/<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path("reports/staff/", views.StaffOnlyReportView.as_view(), name="staff_report"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
]
