from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from api.serializers.alarms import AlarmGetSerializer
from conf.settings.rest_framework import REST_FRAMEWORK
from models_app.models import Alarm, User


class AlarmGetView(APIView):

    def get(self, request, *args, **kwargs):
        alarm_type = request.GET.get("alarm_type")
        user = User.objects.first()
        if alarm_type == "personal":
            print(self.request.user.id)
            alarms = Alarm.objects.filter(user_id=user.id)
        else:
            alarms = Alarm.objects.exclude(user_id=user.id).all()

        paginator = PageNumberPagination()
        paginator.page_size = REST_FRAMEWORK.get("PAGE_SIZE") or 20
        alarms = paginator.paginate_queryset(alarms, request)
        return paginator.get_paginated_response(AlarmGetSerializer(alarms, many=True).data)
