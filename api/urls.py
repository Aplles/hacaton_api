from django.urls import path

from .views.alarms import AlarmGetView
from .views.default_settings import GetDefaultSettingView
from .views.map import ListMapPointsView
from .views.subscribers import DeleteSubscriberView, ListCreateSubscriberView
from .views.test import TestView
from .views.user import ClearUserView, GetUpdateClearUserSettingView, InfoUserView, UserAIAnalyseUpdateView

urlpatterns = [
    path("test/", TestView.as_view()),
    path("user/info/", InfoUserView.as_view()),
    path("user/ai_analyse/", UserAIAnalyseUpdateView.as_view()),
    path("user/clear/", ClearUserView.as_view()),
    path("user/settings/", GetUpdateClearUserSettingView.as_view()),
    path("default_settings/", GetDefaultSettingView.as_view()),
    path("subscribers/", ListCreateSubscriberView.as_view()),
    path("subscribers/<uuid:uuid>/", DeleteSubscriberView.as_view()),
    path("alarms/", AlarmGetView.as_view()),
    path("map/alarms/", ListMapPointsView.as_view()),
]
