from rest_framework import serializers

from models_app.models import DefaultAlarmConf


class DefaultAlarmConfSerializer(serializers.ModelSerializer):

    class Meta:
        model = DefaultAlarmConf
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
