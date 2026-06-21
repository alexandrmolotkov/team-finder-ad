from django.contrib import admin

from django.urls import path, include

from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('projects:project_list')),
    path('admin/', admin.site.urls),
    path('projects/', include(('projects.urls', 'projects'), namespace='projects')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
]
