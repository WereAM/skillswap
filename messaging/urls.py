from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # to all conversations
    path('', views.inbox, name='inbox'),
    #  to a specific conversation thread
    path('<str:username>/', views.conversation, name='conversation'),
]