from django.db import migrations


DEFAULT_CATEGORIES = ("Work", "Personal", "Study", "Health", "Finance", "Home")


def create_default_categories(apps, schema_editor):
    Category = apps.get_model("tasks", "Category")
    database = schema_editor.connection.alias

    for name in DEFAULT_CATEGORIES:
        Category.objects.using(database).get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0002_tag_task_tags_taskalert"),
    ]

    operations = [
        migrations.RunPython(create_default_categories, migrations.RunPython.noop),
    ]
