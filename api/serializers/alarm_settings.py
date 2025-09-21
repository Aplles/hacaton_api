from rest_framework import serializers

from models_app.models import UserAlarmConf


class UserAlarmConfSerializer(serializers.ModelSerializer):
    speed = serializers.IntegerField(required=True)
    speed_weight = serializers.FloatField(required=True)
    magnetic = serializers.IntegerField(required=True)
    magnetic_weight = serializers.FloatField(required=True)
    scatter_area = serializers.FloatField(required=True)
    scatter_weight = serializers.FloatField(required=True)

    class Meta:
        model = UserAlarmConf
        fields = (
            "id",
            "speed",
            "speed_weight",
            "magnetic",
            "magnetic_weight",
            "scatter_area",
            "scatter_weight",
            "created_at",
            "updated_at",
        )
