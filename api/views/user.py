from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class InfoUserView(APIView):

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "code": request.user.code,
                "codes": request.user.codes,
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
