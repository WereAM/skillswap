from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # to all conversations
    path('', views.inbox, name='inbox'),
    #  to a specific conversation thread
    path('<str:username>/', views.conversation, name='conversation'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_read, name='mark_read'),
    path('notifications/read-all/', views.mark_all_read, name='mark_all_read'),
]