import random
import time

from django.db.models.signals import post_save

from models_app.models import Alarm, User


def generate_data():
    print("Начало генерации данных")
    data = []
    count = random.randint(5, 15)

    user = User.objects.first()
    if not user:
        return

    for _ in range(count):
        data.append(
            Alarm(
                speed=random.randint(200, 1000),  # Скорость (в км/x),
                magnetic=random.uniform(0.01, 5.0),  # МП - магнитное поле (float),
                scatter_area=random.uniform(
                    2000, 15000
                ),  # ЭПР - эффективное площадь рассеяния (метры кубические) (float),
                user_id=user.id,
            )
        )

    alarms = Alarm.objects.bulk_create(data)
    for alarm in alarms:
        post_save.send(sender=Alarm, instance=alarm, created=True)
    print("Генерация данных завершена")

    time_delay = random.randint(10, 15)
    time.sleep(time_delay * 60)

    return generate_data()
