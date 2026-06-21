from django.views.generic import CreateView, DetailView, UpdateView, ListView, FormView, View

from django.contrib.auth import login, logout

from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy

from django.shortcuts import redirect

from django.db.models import Q

from .models import User

from .forms import UserRegistrationForm, UserLoginForm, UserEditForm, ChangePasswordForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class UserDetailView(DetailView):
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'users/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:user_detail', kwargs={'pk': self.request.user.pk})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('projects:project_list')


class UsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    paginate_by = 12
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_value = self.request.GET.get('filter')

        if not self.request.user.is_authenticated or not filter_value:
            return queryset

        if filter_value == 'owners-of-favorite-projects':
            favorite_project_ids = self.request.user.favorites.values_list('id', flat=True)
            return queryset.filter(owned_projects__id__in=favorite_project_ids).distinct()

        elif filter_value == 'owners-of-participating-projects':
            my_participated_project_ids = self.request.user.participated_projects.values_list('id', flat=True)
            return queryset.filter(owned_projects__id__in=my_participated_project_ids).distinct()

        elif filter_value == 'interested-in-my-projects':
            my_project_ids = self.request.user.owned_projects.values_list('id', flat=True)
            return queryset.filter(favorites__id__in=my_project_ids).distinct()

        elif filter_value == 'participants-of-my-projects':
            my_project_ids = self.request.user.owned_projects.values_list('id', flat=True)
            return queryset.filter(participated_projects__id__in=my_project_ids).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_filter'] = self.request.GET.get('filter', '')
        return context


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('user_detail')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data['new_password1']
        user.set_password(new_password)
        user.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:user_detail', kwargs={'pk': self.request.user.pk})
