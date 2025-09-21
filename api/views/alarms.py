from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.alarms import AlarmGetSerializer
from conf.settings.rest_framework import REST_FRAMEWORK
from models_app.models import Alarm


class AlarmGetView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        alarm_type = request.GET.get("alarm_type")
        if alarm_type == "personal":
            print(self.request.user.id)
            alarms = Alarm.objects.filter(user_id=user.id).order_by("-created_at")
        else:
            alarms = Alarm.objects.exclude(user_id=user.id).all().order_by("-created_at")

        start_time = request.query_params.get("start_time")
        if start_time:
            alarms = alarms.filter(created_at__gte=start_time)
            return Response(AlarmGetSerializer(alarms, many=True).data)

        paginator = PageNumberPagination()
        paginator.page_size = REST_FRAMEWORK.get("PAGE_SIZE") or 20
        alarms = paginator.paginate_queryset(alarms, request)
        return paginator.get_paginated_response(
            AlarmGetSerializer(alarms, many=True).data
        )
