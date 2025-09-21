from django.contrib.auth.models import AbstractUser
from django.db import models

from models_app.models import BaseModel


class User(AbstractUser, BaseModel):
    code = models.UUIDField(unique=True, verbose_name="Уникальный код")
    codes = models.JSONField(
        default=list, blank=True, verbose_name="Коды известных пользователей"
    )

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
