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
        verbose_name="Еденицы измерения магнитного поля",
    )
    scatter_area = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Eденицы измерения площади разброса",
    )
    speed_weight = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Скорость (км/ч) - вес",
    )
    magnetic_weight = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Еденицы измерения магнитного поля - вес",
    )
    scatter_weight = models.UUIDField(
        blank=True,
        null=True,
        verbose_name="Eденицы измерения площади разброса - вес",
    )

    class Meta:
        db_table = "user_alarm_confs"
        verbose_name = "Настройки предупреждений пользователя"
        verbose_name_plural = "Настройки предупреждений пользователя"
