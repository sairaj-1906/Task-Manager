from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Task


class TaskListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="test-pass-123")
        self.other_user = User.objects.create_user(
            username="sam", password="test-pass-123"
        )
        self.category = Category.objects.create(name="Work")
        self.client.force_login(self.user)

    def test_search_and_filters_return_only_matching_owned_tasks(self):
        matching_task = Task.objects.create(
            title="Prepare launch notes",
            description="Write the release checklist",
            category=self.category,
            priority=Task.Priority.HIGH,
            owner=self.user,
        )
        Task.objects.create(
            title="Prepare launch notes",
            priority=Task.Priority.HIGH,
            owner=self.other_user,
        )
        Task.objects.create(
            title="Buy groceries",
            priority=Task.Priority.HIGH,
            owner=self.user,
        )
        Task.objects.create(
            title="Prepare launch notes",
            priority=Task.Priority.LOW,
            owner=self.user,
        )

        response = self.client.get(
            reverse("task_list"),
            {
                "q": "release",
                "status": "open",
                "priority": Task.Priority.HIGH,
                "category": str(self.category.pk),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["tasks"]), [matching_task])

    def test_pagination_links_preserve_active_filters(self):
        for index in range(11):
            Task.objects.create(
                title=f"Planning task {index}",
                priority=Task.Priority.MEDIUM,
                owner=self.user,
            )

        response = self.client.get(
            reverse("task_list"), {"q": "Planning", "status": "open", "page": "1"}
        )

        self.assertEqual(response.context["tasks"].count(), 10)
        self.assertIn("q=Planning", response.context["next_page_url"])
        self.assertIn("status=open", response.context["next_page_url"])
        self.assertIn("page=2", response.context["next_page_url"])


class DashboardViewTests(TestCase):
    def test_dashboard_summarizes_progress_and_upcoming_tasks(self):
        user = User.objects.create_user(username="alex", password="test-pass-123")
        today = timezone.localdate()
        completed_task = Task.objects.create(
            title="Finished task", is_complete=True, owner=user
        )
        overdue_task = Task.objects.create(
            title="Overdue task", due_date=today - timezone.timedelta(days=1), owner=user
        )
        upcoming_task = Task.objects.create(
            title="Upcoming task", due_date=today + timezone.timedelta(days=1), owner=user
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], 3)
        self.assertEqual(response.context["completed"], 1)
        self.assertEqual(response.context["pending"], 2)
        self.assertEqual(response.context["overdue"], 1)
        self.assertEqual(response.context["completion_percentage"], 33)
        self.assertEqual(
            list(response.context["upcoming_tasks"]), [overdue_task, upcoming_task]
        )
        self.assertNotIn(completed_task, response.context["upcoming_tasks"])
