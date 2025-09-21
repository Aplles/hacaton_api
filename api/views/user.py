from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.alarm_settings import UserAlarmConfSerializer
from models_app.models import UserAlarmConf


class InfoUserView(APIView):

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "code": request.user.code,
                "codes": request.user.codes,
                "ai_analyse_enabled": request.user.ai_analyse_enabled
            },
            status=status.HTTP_200_OK,
        )


class ClearUserView(APIView):

    def post(self, request, *args, **kwargs):
        request.user.codes = []
        request.user.save()
        return Response(
            {"detail": "Информация успешно очистилась"},
            status=status.HTTP_200_OK,
        )


class GetUpdateClearUserSettingView(APIView):

    def get(self, request, *args, **kwargs):
        return Response(
            UserAlarmConfSerializer(UserAlarmConf.get_solo()).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        user_alarm_conf = UserAlarmConf.get_solo()
        for field in user_alarm_conf._meta.fields:
            if field.name not in ['id', 'pk', 'created_at', 'updated_at']:
                setattr(user_alarm_conf, field.name, field.get_default())
        user_alarm_conf.save()
        return Response(
            UserAlarmConfSerializer(user_alarm_conf).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        user_alarm_conf = UserAlarmConf.get_solo()
        user_alarm_conf.ai_analyse_enabled = request.user.ai_analyse_enabled
        serializer = UserAlarmConfSerializer(user_alarm_conf, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            UserAlarmConfSerializer(user_alarm_conf).data,
            status=status.HTTP_200_OK,
        )


class UserAIAnalyseUpdateView(APIView):

    def patch(self, request, *args, **kwargs):
        ai_analyse_enabled = request.data.get("ai_analyse_enabled")
        if not isinstance(ai_analyse_enabled, bool):
            return Response(
                {"detail": "ai_analyse_enabled должен быть типа bool"}, status=status.HTTP_400_BAD_REQUEST
            )
        request.user.ai_analyse_enabled = request.data.get("ai_analyse_enabled")
        request.user.save()
        return Response({"detail": "AI-анализ успешно обновлен"}, status=status.HTTP_200_OK)
