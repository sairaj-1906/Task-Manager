from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Tag, Task


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:             # type: ignore
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class TaskForm(forms.ModelForm):
    tags_text = forms.CharField(
        label="Tags",
        required=False,
        max_length=500,
        help_text="Separate tags with commas.",
    )

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "category",
            "priority",
            "due_date",
            "is_complete",
        ]
        labels = {"is_complete": "Mark as Completed"}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags_text"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )
        else:
            self.fields.pop("is_complete")

    def clean_tags_text(self):
        names = [
            name.strip()
            for name in self.cleaned_data["tags_text"].split(",")
            if name.strip()
        ]
        if any(len(name) > 50 for name in names):
            raise forms.ValidationError("Tags must be 50 characters or fewer.")
        return self.cleaned_data["tags_text"]

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()
            self._save_m2m_with_tags()
        else:
            self.save_m2m = self._save_m2m_with_tags
        return task

    def _save_m2m_with_tags(self):
        tag_names = []
        seen_names = set()
        for raw_name in self.cleaned_data["tags_text"].split(","):
            name = raw_name.strip()
            if name and name.casefold() not in seen_names:
                seen_names.add(name.casefold())
                tag_names.append(name)

        tags = []
        for name in tag_names:
            tag = Tag.objects.filter(name__iexact=name).first()
            if tag is None:
                tag = Tag.objects.create(name=name)
            tags.append(tag)
        self.instance.tags.set(tags)
