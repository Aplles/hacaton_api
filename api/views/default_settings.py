from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.default_settings import DefaultAlarmConfSerializer
from models_app.models import DefaultAlarmConf


class GetDefaultSettingView(APIView):

    def get(self, request, *args, **kwargs):
        return Response(
            DefaultAlarmConfSerializer(DefaultAlarmConf.get_solo()).data,
            status=status.HTTP_200_OK
        )
