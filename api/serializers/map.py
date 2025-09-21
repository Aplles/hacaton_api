from rest_framework import serializers

from api.constants import RESULT_MAPPER
from models_app.models import Alarm


class ListMapPointSerializer(serializers.ModelSerializer):
    grade_humanize = serializers.SerializerMethodField()

    def get_grade_humanize(self, obj):
        if not obj.grade:
            return None
        grade_description = "".join(
            [
                RESULT_MAPPER[key]
                for key in RESULT_MAPPER.keys()
                if key[0] <= obj.grade <= key[1]
            ]
        )
        return f"{grade_description} ({round(obj.grade)}%)"

    class Meta:
        model = Alarm
        fields = (
            "latitude",
            "longitude",
            "grade",
            "grade_humanize",
        )
