from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default auth groups: Managers (Full task permissions) and Members (Basic add/remove)"

    def handle(self, *args: Any, **options):
        managers, _ = Group.objects.get_or_create(name="Manager")
        members, _ = Group.objects.get_or_create(name="Members")

        task_perms = Permission.objects.filter(content_type__app_label="tasks")

        managers.permissions.set(task_perms)

        member_codenames = ["add_task", "view_task", "change_task"]
        members.permissions.set(task_perms.filter(codename__in=member_codenames))

        self.stdout.write(
            self.style.SUCCESS("Groups 'Managers' and 'Members' created/updated.")
        )
