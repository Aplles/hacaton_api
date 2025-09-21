import numpy as np
import tensorflow as tf

from django.db.models.signals import post_save
from django.dispatch import receiver

from models_app.models.alarm.models import Alarm
from models_app.models.default_alarm_conf.models import DefaultAlarmConf
from models_app.models.user_alarm_conf.models import UserAlarmConf
from models_app.models.user.models import User
ai_model = None


def create_ai_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(3,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='linear')
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def train_ai_model():
    global ai_model

    historical_data = Alarm.objects.filter(grade__isnull=False)[:1000]

    if len(historical_data) < 20:
        return None

    X = np.array([[a.speed, a.magnetic, a.scatter_area] for a in historical_data])
    y = np.array([a.grade for a in historical_data])

    ai_model = create_ai_model()
    ai_model.fit(X, y, epochs=10, verbose=0)

    return ai_model


def algo_calculate_grade(sender, instance, **kwargs):
    alarm_conf = (
        UserAlarmConf.objects
        .filter(
            speed__isnull=False,
            magnetic__isnull=False,
            scatter_area__isnull=False,
            speed_weight__isnull=False,
            magnetic_weight__isnull=False,
            scatter_weight__isnull=False,
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


def ai_calculate_grade(sender, instance, **kwargs):
    if ai_model is None:
        train_ai_model()

    if ai_model:
        features = np.array([[instance.speed, instance.magnetic, instance.scatter_area]])
        ai_prediction = ai_model.predict(features, verbose=0)[0][0]

        Alarm.objects.filter(pk=instance.pk).update(grade=+(ai_prediction * 0.3), ai_processed=True)
    else:
        algo_calculate_grade(sender, instance, **kwargs)


@receiver(post_save, sender=Alarm)
def calculate_grade(sender, instance, **kwargs):
    user = User.objects.first()
    if user.ai_analyse_enabled:
        ai_calculate_grade(sender, instance, **kwargs)
    else:
        algo_calculate_grade(sender, instance, **kwargs)
