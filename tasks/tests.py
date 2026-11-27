from django.core import mail
from django.core.management import call_command
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TaskForm
from .models import Category, Task, TaskAlert


class TaskListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="test-pass-123")
        self.other_user = User.objects.create_user(
            username="sam", password="test-pass-123"
        )
        self.category, _ = Category.objects.get_or_create(name="Work")
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

    def test_sorting_and_tag_filter_are_applied_together(self):
        urgent = Task.objects.create(
            title="Urgent",
            priority=Task.Priority.HIGH,
            due_date=timezone.localdate() + timezone.timedelta(days=2),
            owner=self.user,
        )
        urgent.tags.create(name="Launch")
        Task.objects.create(
            title="Lower priority",
            priority=Task.Priority.LOW,
            owner=self.user,
        )
        another_urgent = Task.objects.create(
            title="Another urgent",
            priority=Task.Priority.HIGH,
            owner=self.user,
        )
        another_urgent.tags.create(name="Support")

        response = self.client.get(
            reverse("task_list"),
            {"tag": str(urgent.tags.get().pk), "sort": "priority"},
        )

        self.assertEqual(list(response.context["tasks"]), [urgent])
        self.assertEqual(response.context["sort_order"], "priority")

    def test_invalid_sort_falls_back_to_newest_first(self):
        older = Task.objects.create(title="Older", owner=self.user)
        newer = Task.objects.create(title="Newer", owner=self.user)

        response = self.client.get(reverse("task_list"), {"sort": "not-a-sort"})

        self.assertEqual(list(response.context["tasks"]), [newer, older])
        self.assertEqual(response.context["sort_order"], "-created_at")

    def test_priority_and_due_date_sorting(self):
        low = Task.objects.create(
            title="Low",
            priority=Task.Priority.LOW,
            due_date=timezone.localdate() + timezone.timedelta(days=3),
            owner=self.user,
        )
        high = Task.objects.create(
            title="High",
            priority=Task.Priority.HIGH,
            due_date=timezone.localdate() + timezone.timedelta(days=2),
            owner=self.user,
        )
        medium = Task.objects.create(
            title="Medium",
            priority=Task.Priority.MEDIUM,
            owner=self.user,
        )

        priority_response = self.client.get(
            reverse("task_list"), {"sort": "priority"}
        )
        due_date_response = self.client.get(
            reverse("task_list"), {"sort": "due_date"}
        )

        self.assertEqual(
            list(priority_response.context["tasks"]), [high, medium, low]
        )
        self.assertEqual(
            list(due_date_response.context["tasks"]), [high, low, medium]
        )

    def test_task_actions_render_as_accessible_links(self):
        task = Task.objects.create(title="Planning task", owner=self.user)

        response = self.client.get(reverse("task_list"))

        self.assertContains(
            response,
            f'href="{reverse("task_update", args=[task.pk])}" title="Edit {task.title}" aria-label="Edit {task.title}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("task_delete", args=[task.pk])}" class="delete-action" title="Delete {task.title}" aria-label="Delete {task.title}"',
        )


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
        self.assertEqual(
            list(response.context["alert_tasks"]), [overdue_task, upcoming_task]
        )


class TaskFormTagTests(TestCase):
    def test_completion_control_is_only_available_for_existing_tasks(self):
        user = User.objects.create_user(username="alex", password="test-pass-123")
        task = Task.objects.create(title="Existing task", owner=user)

        self.assertNotIn("is_complete", TaskForm().fields)
        self.assertIn("is_complete", TaskForm(instance=task).fields)

    def test_new_task_ignores_submitted_completion_value(self):
        form = TaskForm(
            data={
                "title": "Plan launch",
                "description": "",
                "category": "",
                "priority": Task.Priority.MEDIUM,
                "due_date": "",
                "is_complete": "on",
                "tags_text": "",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        task = form.save(commit=False)

        self.assertFalse(task.is_complete)

    def test_default_categories_are_available_for_new_tasks(self):
        category_names = set(
            TaskForm().fields["category"].queryset.values_list("name", flat=True)
        )

        default_categories = {
            "Work",
            "Personal",
            "Study",
            "Health",
            "Finance",
            "Home",
        }
        self.assertTrue(default_categories <= category_names)

    def test_form_creates_and_deduplicates_tags(self):
        user = User.objects.create_user(username="alex", password="test-pass-123")
        form = TaskForm(
            data={
                "title": "Plan launch",
                "description": "",
                "category": "",
                "priority": Task.Priority.MEDIUM,
                "due_date": "",
                "tags_text": "Work, urgent, work",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        task = form.save(commit=False)
        task.owner = user
        task.save()
        form.save_m2m()

        self.assertEqual(
            list(task.tags.order_by("name").values_list("name", flat=True)),
            ["Work", "urgent"],
        )

    def test_form_rejects_tag_names_over_model_limit(self):
        form = TaskForm(
            data={
                "title": "Plan launch",
                "description": "",
                "category": "",
                "priority": Task.Priority.MEDIUM,
                "due_date": "",
                "tags_text": "x" * 51,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("tags_text", form.errors)


class TaskAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="test-pass-123")
        self.other_user = User.objects.create_user(
            username="sam", password="test-pass-123"
        )

    def test_api_requires_login_and_returns_json(self):
        response = self.client.get(reverse("api_task_list"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"error": "Authentication required."})

    def test_create_patch_and_delete_task(self):
        self.client.force_login(self.user)
        create_response = self.client.post(
            reverse("api_task_list"),
            data={
                "title": "Prepare release",
                "priority": Task.Priority.HIGH,
                "due_date": "2026-12-01",
                "tags": ["Release", "Work"],
            },
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()
        self.assertEqual(created["owner_id"], self.user.pk)
        self.assertEqual(created["tags"], ["Release", "Work"])
        task_url = reverse("api_task_detail", args=[created["id"]])

        patch_response = self.client.patch(
            task_url,
            data={"is_complete": True, "tags": ["Shipped"]},
            content_type="application/json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertTrue(patch_response.json()["is_complete"])
        self.assertEqual(patch_response.json()["tags"], ["Shipped"])

        delete_response = self.client.delete(task_url)
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=created["id"]).exists())

    def test_api_list_filters_and_never_exposes_other_users_tasks(self):
        self.client.force_login(self.user)
        matching = Task.objects.create(
            title="Prepare release",
            priority=Task.Priority.HIGH,
            owner=self.user,
        )
        tag = matching.tags.create(name="Release")
        Task.objects.create(title="Prepare release", owner=self.other_user)

        response = self.client.get(
            reverse("api_task_list"),
            {"q": "Release", "priority": Task.Priority.HIGH, "tag": str(tag.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], matching.pk)

    def test_api_rejects_malformed_and_unknown_fields(self):
        self.client.force_login(self.user)

        malformed = self.client.post(
            reverse("api_task_list"), data="{", content_type="application/json"
        )
        unknown = self.client.post(
            reverse("api_task_list"),
            data={"title": "Test", "owner_id": self.other_user.pk},
            content_type="application/json",
        )

        self.assertEqual(malformed.status_code, 400)
        self.assertEqual(unknown.status_code, 400)

    def test_api_hides_tasks_owned_by_another_user(self):
        task = Task.objects.create(title="Private task", owner=self.other_user)
        self.client.force_login(self.user)

        response = self.client.get(reverse("api_task_detail", args=[task.pk]))

        self.assertEqual(response.status_code, 404)

    def test_api_put_requires_a_full_task_representation(self):
        task = Task.objects.create(title="Private task", owner=self.user)
        self.client.force_login(self.user)

        response = self.client.put(
            reverse("api_task_detail", args=[task.pk]),
            data={"title": "Replacement"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        task.refresh_from_db()
        self.assertEqual(task.title, "Private task")

    def test_api_mutations_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)

        response = client.post(
            reverse("api_task_list"),
            data={"title": "No token"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)


class TaskAlertCommandTests(TestCase):
    def test_sends_due_and_overdue_emails_only_once(self):
        user = User.objects.create_user(
            username="alex", email="alex@example.com", password="test-pass-123"
        )
        today = timezone.localdate()
        Task.objects.create(title="Due today", due_date=today, owner=user)
        Task.objects.create(
            title="Due tomorrow",
            due_date=today + timezone.timedelta(days=1),
            owner=user,
        )
        Task.objects.create(
            title="Overdue",
            due_date=today - timezone.timedelta(days=1),
            owner=user,
        )
        Task.objects.create(
            title="Not due yet",
            due_date=today + timezone.timedelta(days=2),
            owner=user,
        )

        with self.settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
        ):
            call_command("send_task_alerts")
            call_command("send_task_alerts")

        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(TaskAlert.objects.filter(sent_at__isnull=False).count(), 3)
