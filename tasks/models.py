from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    is_complete = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)

    # Object-level authorization: only the owner(or staff/admin) may edit/delete
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            ("can_mark_complete", "Can mark task as complete"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("task_detail", kwargs={"pk": self.pk})


class TaskAlert(models.Model):
    class Kind(models.TextChoices):
        DUE_SOON = "DUE_SOON", "Due soon"
        OVERDUE = "OVERDUE", "Overdue"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="alerts")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    due_date = models.DateField()
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["task", "kind", "due_date"], name="unique_task_alert"
            )
        ]
