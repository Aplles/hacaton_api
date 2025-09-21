from django.db import models
from solo.models import SingletonModel

from models_app.models.base.models import BaseModel


class DefaultAlarmConf(SingletonModel, BaseModel):
    speed = models.IntegerField(
        verbose_name="Скорость (км/ч)",
    )
    magnetic = models.IntegerField(
        verbose_name="Магнитное поле",
    )
    scatter_area = models.FloatField(
        verbose_name="Эффективное площадь рассеяния",
    )
    speed_weight = models.FloatField(
        verbose_name="Скорость (км/ч) - вес",
    )
    magnetic_weight = models.FloatField(
        verbose_name="Магнитного поле - вес",
    )
    scatter_weight = models.FloatField(
        verbose_name="Эффективное площадь рассеяния - вес",
    )

    class Meta:
        db_table = "default_alarm_confs"
        verbose_name = "Настройки предупреждений по умолчанию"
        verbose_name_plural = "Настройки предупреждений по умолчанию"
