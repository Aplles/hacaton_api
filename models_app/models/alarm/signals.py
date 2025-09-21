from django.db.models.signals import post_save
from django.dispatch import receiver

from models_app.models.alarm.models import Alarm
from models_app.models.default_alarm_conf.models import DefaultAlarmConf
from models_app.models.user_alarm_conf.models import UserAlarmConf


@receiver(post_save, sender=Alarm)
def calculate_grade(sender, instance, **kwargs):
    print("!" * 50)
    alarm_conf = (
        UserAlarmConf.objects
        .filter(
            speed__isnull=False,
            magnetic__isnull=False,
            scatter_area__isnull=False,
        )
        .first()
    )
    if not alarm_conf:
        alarm_conf = DefaultAlarmConf.get_solo()

    normalized_data = {
        "speed": instance.speed / alarm_conf.speed,
        "magnetic": instance.magnetic / alarm_conf.magnetic,
        "scatter_area": instance.scatter_area / alarm_conf.scatter_area,
    }

    contributions_data = {
        "speed": normalized_data["speed"] * alarm_conf.speed_weight,
        "magnetic": normalized_data["magnetic"] * alarm_conf.magnetic_weight,
        "scatter_area": normalized_data["scatter_area"] * alarm_conf.scatter_weight,
    }

    total_contributions = sum(contributions_data.values())
    total_weights = (
        alarm_conf.speed_weight + alarm_conf.magnetic_weight + alarm_conf.scatter_weight
    )

    result_in_percentage = (total_contributions / total_weights) * 100

    instance.grade = result_in_percentage
    Alarm.objects.filter(pk=instance.pk).update(grade=result_in_percentage)
    # instance.save()
