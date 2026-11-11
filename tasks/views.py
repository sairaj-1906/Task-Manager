from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from .forms import SignUpForm, TaskForm
from .models import Category, Task


# =============== Authentication views ===============
class SignUpView(View):
    """Public registration view. Anyone can create an account"""

    template_name = "registration/signup.html"

    def get(self, request):
        form = SignUpForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("task_list")
        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = "login"


# =============== Task views (require login = Authentication) ===============
class TaskListView(LoginRequiredMixin, ListView):
    """Authenticated users see only their own tasks, unless they are staff, in which they can see everything (role-based authorization)."""

    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        qs = Task.objects.select_related("category", "owner")
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)

        self.search_query = self.request.GET.get("q", "").strip()
        self.status_filter = self.request.GET.get("status", "all")
        self.priority_filter = self.request.GET.get("priority", "")
        self.category_filter = self.request.GET.get("category", "")

        if self.search_query:
            qs = qs.filter(
                Q(title__icontains=self.search_query)
                | Q(description__icontains=self.search_query)
            )

        if self.status_filter == "open":
            qs = qs.filter(is_complete=False)
        elif self.status_filter == "completed":
            qs = qs.filter(is_complete=True)
        elif self.status_filter != "all":
            self.status_filter = "all"

        priorities = {choice[0] for choice in Task.Priority.choices}
        if self.priority_filter not in priorities:
            self.priority_filter = ""
        else:
            qs = qs.filter(priority=self.priority_filter)

        if self.category_filter.isdecimal():
            qs = qs.filter(category_id=int(self.category_filter))
        else:
            self.category_filter = ""

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "categories": Category.objects.all(),
                "priority_choices": Task.Priority.choices,
                "search_query": self.search_query,
                "status_filter": self.status_filter,
                "priority_filter": self.priority_filter,
                "category_filter": self.category_filter,
                "today": timezone.localdate(),
            }
        )

        query_params = self.request.GET.copy()
        if context["page_obj"].has_previous():
            query_params["page"] = context["page_obj"].previous_page_number()
            context["previous_page_url"] = f"?{query_params.urlencode()}"
        if context["page_obj"].has_next():
            query_params["page"] = context["page_obj"].next_page_number()
            context["next_page_url"] = f"?{query_params.urlencode()}"
        return context


class TaskDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def test_func(self):
        """Authorization: only the owner or staff may view the detail page."""
        task = self.get_object()
        return self.request.user.is_staff or task.owner_id == self.request.user.id

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to view that task.")
        return redirect("task_list")


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Task created successfully.")
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def test_func(self):
        """Authorization: only the owner or staff may edit."""
        task = self.get_object()
        return self.request.user.is_staff or task.owner_id == self.request.user.id

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit that task.")
        return redirect("task_list")

    def form_valid(self, form):
        messages.success(self.request, "Task updated successfully.")
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("task_list")

    def test_func(self):
        """Authorization: only the owner or staff may delete."""
        task = self.get_object()
        return self.request.user.is_staff or task.owner_id == self.request.user.id

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete that task.")
        return redirect("task_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Task deleted.")
        return super().delete(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, View):
    """A simple home/dashboard page after login."""

    def get(self, request):
        user_tasks = Task.objects.filter(owner=request.user)
        completed = user_tasks.filter(is_complete=True).count()
        total = user_tasks.count()
        today = timezone.localdate()
        context = {
            "total": total,
            "completed": completed,
            "pending": user_tasks.filter(is_complete=False).count(),
            "overdue": user_tasks.filter(
                is_complete=False, due_date__lt=today
            ).count(),
            "completion_percentage": round(completed / total * 100) if total else 0,
            "today": today,
            "upcoming_tasks": user_tasks.filter(
                is_complete=False, due_date__isnull=False
            ).order_by("due_date")[:5],
        }
        return render(request, "tasks/dashboard.html", context)


class StaffOnlyReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Example of ROLE-based authentication (as opposed to object-level): only staff/admin users may access this view at all."""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "Staff access only.")
        return redirect("task_list")

    def get(self, request):
        tasks = Task.objects.select_related("owner", "category").all()
        return render(request, "tasks/staff_report.html", {"tasks": tasks})
