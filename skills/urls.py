from django.urls import path
from . import views

app_name = 'skills'

urlpatterns = [
    path('', views.skill_list, name='list'),
    path('mine/', views.my_skills, name='my_skills'),
    path('add/', views.add_user_skill, name='add'),
    path('<int:pk>/', views.skill_detail, name='details'),
    path('<int:pk>/edit/', views.edit__user_skill, name='edit'),
    path('<int:pk>/delete/', views.delete_user_skill, name='delete'),
]