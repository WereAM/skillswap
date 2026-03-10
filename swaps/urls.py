from django.urls import path
from . import views

app_name = 'swaps'

urlpatterns = [
    # send a swap request from skill detail page
    path('create/<int:skill_id>/', views.create_swap, name='create'),
    # received requests
    path('inbox/', views.inbox, name='inbox'),
    # sent requests
    path('sent/', views.sent_requests, name='sent'),
    # details of a single swap request
    path('<int:pk>/', views.swap_detail, name='detail'),
    # swap actions
    path('<int:pk>/accept/', views.accept_swap, name='accept'),
    path('<int:pk>/deny/', views.deny_swap, name='deny'),
    path('<int:pk>/cancel/', views.cancel_swap, name='cancel'),
    
]