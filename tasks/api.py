import json
from json import JSONDecodeError
from typing import Any

from django.db.models import Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .forms import TaskForm
from .models import Task
from .querysets import order_tasks


class AuthenticatedJSONView(View):
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)
        return super().dispatch(request, *args, **kwargs)


def _visible_tasks(user):
    queryset = Task.objects.select_related("category", "owner").prefetch_related("tags")
    if not user.is_staff:
        queryset = queryset.filter(owner=user)
    return queryset


def _serialize_task(task):
    return {
        "id": task.pk,
        "title": task.title,
        "description": task.description,
        "category": (
            {"id": task.category_id, "name": task.category.name}
            if task.category_id
            else None
        ),
        "tags": [tag.name for tag in task.tags.all()],
        "priority": task.priority,
        "is_complete": task.is_complete,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "owner_id": task.owner_id,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.update_at.isoformat(),
    }


def _parse_payload(request: HttpRequest) -> dict[str, Any] | JsonResponse:
    try:
        payload = json.loads(request.body)
    except (JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Request body must be valid JSON."}, status=400
        )
    if not isinstance(payload, dict):
        return JsonResponse({"error": "JSON body must be an object."}, status=400)
    return payload


def _task_form(payload: dict[str, Any], instance=None) -> TaskForm | JsonResponse:
    allowed_fields = {
        "title",
        "description",
        "category_id",
        "tags",
        "priority",
        "is_complete",
        "due_date",
    }
    unknown_fields = set(payload) - allowed_fields
    if unknown_fields:
        return JsonResponse(
            {"error": "Unknown fields.", "fields": sorted(unknown_fields)}, status=400
        )

    tags = payload.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        return JsonResponse(
            {"error": "The tags field must be a list of strings."}, status=400
        )

    form_data = {}
    if instance is not None:
        form_data = {
            "title": instance.title,
            "description": instance.description,
            "category": instance.category_id or "",
            "tags_text": ", ".join(instance.tags.values_list("name", flat=True)),
            "priority": instance.priority,
            "is_complete": instance.is_complete,
            "due_date": instance.due_date.isoformat() if instance.due_date else "",
        }

    for key in allowed_fields - {"tags", "category_id"}:
        if key in payload:
            form_data[key] = payload[key]
    if "category_id" in payload:
        form_data["category"] = payload["category_id"] or ""
    if "tags" in payload:
        form_data["tags_text"] = ", ".join(tags)

    form = TaskForm(form_data, instance=instance)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
    return form


def _list_tasks(request):
    queryset = _visible_tasks(request.user)
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(tags__name__icontains=query)
        )

    status = request.GET.get("status", "")
    if status == "open":
        queryset = queryset.filter(is_complete=False)
    elif status == "completed":
        queryset = queryset.filter(is_complete=True)

    priority = request.GET.get("priority", "")
    if priority in Task.Priority.values:
        queryset = queryset.filter(priority=priority)

    category = request.GET.get("category", "")
    if category.isdecimal():
        queryset = queryset.filter(category_id=int(category))

    tag = request.GET.get("tag", "")
    if tag.isdecimal():
        queryset = queryset.filter(tags__id=int(tag))

    queryset, _ = order_tasks(queryset, request.GET.get("sort", "-created_at"))
    return queryset


class TaskCollectionAPI(AuthenticatedJSONView):
    def get(self, request):
        try:
            limit = int(request.GET.get("limit", "50"))
            offset = int(request.GET.get("offset", "0"))
        except ValueError:
            return JsonResponse(
                {"error": "limit and offset must be integers."}, status=400
            )
        if not 1 <= limit <= 100 or offset < 0:
            return JsonResponse(
                {"error": "limit must be 1–100 and offset must be non-negative."},
                status=400,
            )

        queryset = _list_tasks(request)
        total = queryset.count()
        tasks = [
            _serialize_task(task) for task in queryset[offset : offset + limit]
        ]
        next_offset = offset + len(tasks)
        return JsonResponse(
            {
                "count": total,
                "next_offset": next_offset if next_offset < total else None,
                "results": tasks,
            }
        )

    def post(self, request):
        payload = _parse_payload(request)
        if isinstance(payload, JsonResponse):
            return payload
        form = _task_form(payload)
        if isinstance(form, JsonResponse):
            return form
        task = form.save(commit=False)
        task.owner = request.user
        task.save()
        form.save_m2m()
        return JsonResponse(_serialize_task(task), status=201)


class TaskDetailAPI(AuthenticatedJSONView):
    def get_task(self, request, pk):
        return get_object_or_404(_visible_tasks(request.user), pk=pk)

    def get(self, request, pk):
        return JsonResponse(_serialize_task(self.get_task(request, pk)))

    def put(self, request, pk):
        return self._update(request, pk)

    def patch(self, request, pk):
        return self._update(request, pk)

    def _update(self, request, pk):
        task = self.get_task(request, pk)
        payload = _parse_payload(request)
        if isinstance(payload, JsonResponse):
            return payload
        if request.method == "PUT":
            required_fields = {
                "title",
                "description",
                "category_id",
                "tags",
                "priority",
                "is_complete",
                "due_date",
            }
            missing_fields = required_fields - set(payload)
            if missing_fields:
                return JsonResponse(
                    {
                        "error": "PUT requires all task fields.",
                        "fields": sorted(missing_fields),
                    },
                    status=400,
                )
        form = _task_form(payload, instance=task)
        if isinstance(form, JsonResponse):
            return form
        task = form.save()
        return JsonResponse(_serialize_task(task))

    def delete(self, request, pk):
        task = self.get_task(request, pk)
        task.delete()
        return HttpResponse(status=204)
