from django.db.models import Case, F, IntegerField, QuerySet, When

from .models import Task


SORT_CHOICES = (
    ("-created_at", "Newest first"),
    ("created_at", "Oldest first"),
    ("due_date", "Due date (earliest)"),
    ("-due_date", "Due date (latest)"),
    ("priority", "Priority (high first)"),
    ("-priority", "Priority (low first)"),
    ("title", "Title (A–Z)"),
    ("-title", "Title (Z–A)"),
)


def order_tasks(queryset: QuerySet, sort_order: str) -> tuple[QuerySet, str]:
    valid_orders = set(dict(SORT_CHOICES))
    if sort_order not in valid_orders:
        sort_order = "-created_at"

    if sort_order in {"due_date", "-due_date"}:
        ordering = (
            F("due_date").asc(nulls_last=True)
            if sort_order == "due_date"
            else F("due_date").desc(nulls_last=True)
        )
    elif sort_order == "priority":
        ordering = Case(
            When(priority=Task.Priority.HIGH, then=0),
            When(priority=Task.Priority.MEDIUM, then=1),
            default=2,
            output_field=IntegerField(),
        )
    elif sort_order == "-priority":
        ordering = Case(
            When(priority=Task.Priority.LOW, then=0),
            When(priority=Task.Priority.MEDIUM, then=1),
            default=2,
            output_field=IntegerField(),
        )
    else:
        ordering = sort_order

    return queryset.order_by(ordering, "pk").distinct(), sort_order
