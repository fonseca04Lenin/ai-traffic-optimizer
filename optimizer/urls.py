from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/new/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:pk>/status/', views.job_status_update, name='job_status_update'),

    # Drivers
    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/new/', views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),

    # Routes
    path('routes/', views.route_list, name='route_list'),
    path('routes/optimize/', views.route_optimize, name='route_optimize'),
    path('routes/<int:pk>/', views.route_detail, name='route_detail'),
    path('routes/<int:pk>/delete/', views.route_delete, name='route_delete'),

    # API
    path('api/jobs/', views.api_jobs, name='api_jobs'),
]
