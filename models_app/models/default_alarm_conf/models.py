from solo.models import SingletonModel
from django.db import models

from models_app.models import BaseModel


class DefaultAlarmConf(SingletonModel, BaseModel):
    speed = models.IntegerField(
        verbose_name="Скорость (км/ч)",
    )
    magnetic = models.IntegerField(
        verbose_name="Еденицы измерения магнитного поля",
    )
    scatter_area = models.IntegerField(
        verbose_name="Eденицы измерения площади разброса",
    )
    speed_weight = models.IntegerField(
        verbose_name="Скорость (км/ч) - вес",
    )
    magnetic_weight = models.IntegerField(
        verbose_name="Еденицы измерения магнитного поля - вес",
    )
    scatter_weight = models.UUIDField(
        verbose_name="Eденицы измерения площади разброса - вес",
    )

    class Meta:
        db_table = "default_alarm_confs"
        verbose_name = "Настройки предупреждений по умолчанию"
        verbose_name_plural = "Настройки предупреждений по умолчанию"
