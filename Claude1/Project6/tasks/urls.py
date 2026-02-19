from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.create_task, name='create_task'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/apply/', views.apply_for_task, name='apply_for_task'),
    path('<int:task_id>/complete/', views.complete_task, name='complete_task'),
]
