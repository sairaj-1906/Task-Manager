from django.contrib import admin
from .models import Category, Tag, Task, TaskAlert

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "category",
        "priority",
        "is_complete",
        "due_date",
    )
    list_filter = ("priority", "is_complete", "category", "tags")
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)


@admin.register(TaskAlert)
class TaskAlertAdmin(admin.ModelAdmin):
    list_display = ("task", "kind", "due_date", "sent_at")
    list_filter = ("kind", "sent_at")
    search_fields = ("task__title", "task__owner__username")
