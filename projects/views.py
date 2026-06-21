from django.views.generic import ListView, CreateView, DetailView, UpdateView, View

from django.shortcuts import get_object_or_404, redirect

from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse

from .models import Project

from .forms import ProjectForm


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']
    paginate_by = 12


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.save()
        form.instance.participants.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            is_participating = False
        else:
            project.participants.add(request.user)
            is_participating = True

        return redirect('projects:project_detail', pk=pk)


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        return self.request.user.favorites.all().order_by('-created_at')


class ProjectCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if request.user != project.owner:
            return JsonResponse({'status': 'error', 'message': 'Только автор может завершить проект'}, status=403)

        if project.status != 'open':
            return JsonResponse({'status': 'error', 'message': 'Проект уже завершен'}, status=400)

        project.status = 'closed'
        project.save()

        return JsonResponse({'status': 'ok', 'project_status': 'closed'})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if request.user == project.owner:
            return redirect('project_detail', pk=pk)

        if request.user in project.participants.all():
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)

        project.save()
        return redirect('projects:project_detail', pk=pk)


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        if project in request.user.favorites.all():
            request.user.favorites.remove(project)
            favorited = False
        else:
            request.user.favorites.add(project)
            favorited = True

        return JsonResponse({
            'status': 'ok', 
            'favorited': favorited
        })
