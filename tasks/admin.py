from django.contrib import admin
from .models import Category, Task

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "priority", "is_complete", "due_date")
    list_filter = ("priority", "is_complete", "category")
    search_fields = ("title", "description")
