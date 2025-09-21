from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.map import ListMapPointSerializer
from models_app.models import Alarm


class ListMapPointsView(APIView):

    def get(self, request, *args, **kwargs):
        alarms = Alarm.objects.all()
        try:
            min_grade = int(request.query_params.get("min_grade", ""))
        except ValueError:
            min_grade = None

        try:
            max_grade = int(request.query_params.get("max_grade", ""))
        except ValueError:
            max_grade = None

        if min_grade:
            alarms = alarms.filter(grade__gt=min_grade)
        if max_grade:
            alarms = alarms.filter(grade__lt=max_grade)

        return Response(
            ListMapPointSerializer(alarms, many=True).data,
            status=status.HTTP_200_OK,
        )
