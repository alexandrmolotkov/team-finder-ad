from django.conf import settings
from django.db import models
from django.urls import reverse

from core.constants import (MAX_LENGTH_NAME, MAX_LENGTH_STATUS,
                            PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN)


class Project(models.Model):
    STATUS_CHOICES = [
        (PROJECT_STATUS_OPEN, 'Open'),
        (PROJECT_STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=MAX_LENGTH_NAME, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects', verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    github_url = models.URLField(blank=True, verbose_name='Ссылка на GitHub')
    status = models.CharField(max_length=MAX_LENGTH_STATUS, choices=STATUS_CHOICES, default='PROJECT_STATUS_OPEN', verbose_name='Статус')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='participated_projects', verbose_name='Участники')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})
