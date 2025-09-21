from django.urls import path

from .views.alarms import AlarmGetView
from .views.subscribers import CreateSubscriberView
from .views.test import TestView
from .views.user import ClearUserView, InfoUserView

urlpatterns = [
    path("test/", TestView.as_view()),
    path("user/info/", InfoUserView.as_view()),
    path("user/clear/", ClearUserView.as_view()),
    path("subscribers/", CreateSubscriberView.as_view()),
    path("alarms/", AlarmGetView.as_view()),
]
