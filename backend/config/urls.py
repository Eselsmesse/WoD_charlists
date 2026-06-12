"""Корневой роутинг проекта."""

from django.contrib import admin
from django.urls import include, path

from . import views

api_v1_patterns = [
    path('health/', views.health, name='api-health'),
    path('auth/', include('accounts.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
    path('', include('main.urls')),
]
