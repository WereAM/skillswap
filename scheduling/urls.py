from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    # main calendar view
    path('', views.calendar_view, name='calendar'),
    # schedule a session
    path('schedule/<int:swap_pk>/', views.schedule_session, name='schedule_session'),
    # availability and preferences
    path('availability/', views.set_availability, name='availability'),
    # AJAX/API endpoints
    path('api/check-conflict/', views.api_check_conflict, name='api_check_conflict'),
    path('api/get_suggestions/', views.api_get_suggestions, name='api_get_suggestions'),
]