from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from models_app.models import User


class CreateSubscriberView(APIView):

    def post(self, request, *args, **kwargs):
        user_uuid = request.data.get("user_uuid")
        if not user_uuid:
            raise ValidationError({"detail": "Передайте параметр user_uuid"})
        user = User.objects.first()

        message = "Вы уже подписаны на этого пользователя"
        if user_uuid not in user.codes:
            user.codes.append(user_uuid)
            user.save()
            message = "Вы успешно подписались на пользователя"

        return Response({"info": message}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        user = User.objects.first()
        codes = [{"id": index, "code": code} for index, code in enumerate(user.codes)]
        return Response(codes, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user_uuid = request.data.get("user_uuid")
        if not user_uuid:
            raise ValidationError({"detail": "Передайте параметр user_uuid"})
        user = User.objects.first()

        result = list(set(user.codes) - set([request.data.get("user_uuid")]))
        user.codes = result
        user.save()
        return Response({"info": "Вы успешно отписались от пользователя"}, status=status.HTTP_200_OK)