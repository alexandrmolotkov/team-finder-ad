from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='project_list'),
    path('create-project/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('<int:pk>/toggle-favorite/', views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('<int:pk>/toggle-participate/', views.ToggleParticipateView.as_view(), name='toggle_participate'),
    path('<int:pk>/complete/', views.ProjectCompleteView.as_view(), name='project_complete'),
    path('favorites/', views.FavoritesListView.as_view(), name='favorites_list'),
]
