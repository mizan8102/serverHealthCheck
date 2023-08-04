from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='checkupt'),
    path('api/server-info/', views.server_info_list, name='server-info-list'),
    path('api/create-server-info/', views.create_server_info, name='create-server-info'),
    path('api/server_up_down_check', views.server_up_down_check, name='server_up_down_check'),
    path('api/health-check/', views.SSHHealthCheckAPI.as_view(), name='ssh-health-check'),

]