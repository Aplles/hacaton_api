from rest_framework import serializers

from api.constants import RESULT_MAPPER
from models_app.models import Alarm


class AlarmGetSerializer(serializers.ModelSerializer):
    grade_humanize = serializers.SerializerMethodField()
    other_user_grade_humanize = serializers.SerializerMethodField()

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

    def get_other_user_grade_humanize(self, obj):
        if not obj.other_user_grade:
            return None
        grade_description = "".join(
            [
                RESULT_MAPPER[key]
                for key in RESULT_MAPPER.keys()
                if key[0] <= obj.other_user_grade <= key[1]
            ]
        )
        return f"{grade_description} ({round(obj.other_user_grade)}%)"

    class Meta:
        model = Alarm
        fields = (
            "id",
            "speed",
            "magnetic",
            "scatter_area",
            "grade",
            "grade_humanize",
            "other_user_grade_humanize",
            "created_at",
            "updated_at",
            "user_id",
            "longitude",
            "latitude",
        )
