from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # auth
    path('auth/token/', views.ObtainTokenView.as_view(), name='chronogami_token'),
    path('auth/token/refresh',  TokenRefreshView.as_view(), name='chronogami_token_refresh'),
    path('auth/register-client/', views.RegisterAPIClientView.as_view(), name='chronogami_register_client'),

    # scheduling
    path('scheduling/suggest/', views.SuggestTimesView.as_view(), name='chronogami_suggest'),
    path('scheduling/conflicts', views.ConflictCheckView.as_view(), name='chronogami_conflicts'),
    path('scheduling/availability/<int:user_id>/', views.AvailabilityView.as_view(), name='chronogami_availability'),
    path('scheduling/sessions/<int:user_id>/', views.UserSessionsView.as_view(), name='chronogami_sessions'),
    path('scheduling/timezones/', views.TimezoneListView.as_view(), name='chronogami_timezones'),
]