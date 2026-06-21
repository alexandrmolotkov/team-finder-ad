from django import forms
from django.urls import reverse


class GithubURLMixin:
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url and 'github.com' not in url:
            raise forms.ValidationError('Ссылка должна вести на GitHub')
        return url


class SuccessProjectURLMixin:
    def get_success_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.object.pk})


class SuccessUserURLMixin:
    def get_success_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.request.user.pk})
