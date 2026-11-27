from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils.formats import date_format
from django.utils import timezone

from tasks.models import Task, TaskAlert


class Command(BaseCommand):
    help = "Email reminders for tasks due today, tomorrow, or already overdue."

    def handle(self, *args, **options):
        today = timezone.localdate()
        tomorrow = today + timezone.timedelta(days=1)
        tasks = (
            Task.objects.filter(is_complete=False, due_date__lte=tomorrow)
            .exclude(due_date__isnull=True)
            .select_related("owner")
            .order_by("due_date", "pk")
        )
        sent_count = 0

        for task in tasks:
            kind = (
                TaskAlert.Kind.OVERDUE
                if task.due_date < today
                else TaskAlert.Kind.DUE_SOON
            )
            alert, _created = TaskAlert.objects.get_or_create(
                task=task, kind=kind, due_date=task.due_date
            )
            if alert.sent_at:
                continue
            if not task.owner.email:
                raise CommandError(
                    f"Cannot send an alert for task {task.pk}: the owner has no email address."
                )

            status = "overdue" if kind == TaskAlert.Kind.OVERDUE else "due soon"
            sent = send_mail(
                subject=f"Taskflow reminder: {task.title} is {status}",
                message=(
                    f"Hello {task.owner.get_username()},\n\n"
                    f'Your task "{task.title}" is {status} '
                    f"(due {date_format(task.due_date, 'F j, Y')}).\n\n"
                    "Open Taskflow to review your task."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.owner.email],
                fail_silently=False,
            )
            if sent != 1:
                raise CommandError(f"Email delivery failed for task {task.pk}.")

            alert.sent_at = timezone.now()
            alert.save(update_fields=["sent_at"])
            sent_count += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent_count} task alert(s)."))
