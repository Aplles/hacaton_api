from solo.models import SingletonModel
from django.db import models

from models_app.models import BaseModel


class UserAlarmConf(SingletonModel, BaseModel):
    speed = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Скорость (км/ч)",
    )
    magnetic = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Магнитное поле",
    )
    scatter_area = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Эффективное площадь рассеяния",
    )
    speed_weight = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Скорость (км/ч) - вес",
    )
    magnetic_weight = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Магнитного поле - вес",
    )
    scatter_weight = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Эффективное площадь рассеяния - вес",
    )

    class Meta:
        db_table = "user_alarm_confs"
        verbose_name = "Настройки предупреждений пользователя"
        verbose_name_plural = "Настройки предупреждений пользователя"
