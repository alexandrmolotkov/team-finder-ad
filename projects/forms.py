from django import forms

from core.mixins import GithubURLMixin

from .models import Project


class ProjectForm(GithubURLMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'status': forms.Select(choices=Project.STATUS_CHOICES)
        }
