from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from models_app.models import User


class InfoUser(APIView):

    def get(self, request, *args, **kwargs):
        user = User.objects.first()
        return Response(
            {
                "code": user.code,
                "codes": user.codes,
            },
            status=status.HTTP_200_OK,
        )
