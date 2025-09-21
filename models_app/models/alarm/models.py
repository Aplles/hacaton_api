from django.db import models

from models_app.models.base.models import BaseModel


class Alarm(BaseModel):
    speed = models.IntegerField(
        verbose_name="Скорость (км/ч)",
    )
    magnetic = models.IntegerField(
        verbose_name="Магнитное поле",
    )
    scatter_area = models.IntegerField(
        verbose_name="Эффективное площадь рассеяния",
    )
    latitude = models.FloatField(
        default=0.0,
        verbose_name="Широта",
    )
    longitude = models.FloatField(
        default=0.0,
        verbose_name="Долгота",
    )
    grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Персональная оценка",
    )
    other_user_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Оценка другого пользователя (отправителя)",
    )
    user_id = models.UUIDField(
        verbose_name="ID пользователя",
    )

    class Meta:
        db_table = "alarms"
        verbose_name = "Предупреждение"
        verbose_name_plural = "Предупреждения"
