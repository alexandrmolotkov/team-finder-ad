from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (CreateView, DetailView, ListView, UpdateView,
                                  View)

from core.constants import PAGINATE_BY, PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED
from core.mixins import SuccessProjectURLMixin

from .forms import ProjectForm
from .models import Project


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return super().get_queryset().select_related('owner').prefetch_related(
            Prefetch('participants')
        ).annotate(participants_count=Count('participants'))


class ProjectCreateView(SuccessProjectURLMixin, LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.save()
        form.instance.participants.add(self.request.user)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'

    def get_queryset(self):
        return super().get_queryset().select_related('owner').prefetch_related('participants')


class ProjectUpdateView(SuccessProjectURLMixin, LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        is_participating = project.participants.filter(pk=request.user.pk).exists()
        if is_participating:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)

        # Возвращает не JSON, так как изначально реализацию делал через HTML-форму. Но так всё равно работает
        return redirect('projects:project_detail', pk=pk)


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return self.request.user.favorites.all().select_related('owner').prefetch_related(Prefetch('participants')).annotate(participants_count=Count('participants')).order_by('-created_at')


class ProjectCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if request.user != project.owner:
            return JsonResponse({'status': 'error', 'message': 'Только автор может завершить проект'}, status=HTTPStatus.FORBIDDEN)

        if project.status != PROJECT_STATUS_OPEN:
            return JsonResponse({'status': 'error', 'message': 'Проект уже завершен'}, status=HTTPStatus.BAD_REQUEST)

        project.status = PROJECT_STATUS_CLOSED
        project.save()

        return JsonResponse({'status': 'ok', 'project_status': PROJECT_STATUS_CLOSED})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if request.user == project.owner:
            return redirect('projects:project_detail', pk=pk)

        is_participating = project.participants.filter(pk=request.user.pk).exists()

        if is_participating:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)

        project.save()
        return redirect('projects:project_detail', pk=pk)


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        is_favorited = request.user.favorites.filter(pk=project.pk).exists()

        if is_favorited:
            request.user.favorites.remove(project)
        else:
            request.user.favorites.add(project)

        return JsonResponse({
            'status': 'ok', 
            'favorited': not is_favorited
        })
