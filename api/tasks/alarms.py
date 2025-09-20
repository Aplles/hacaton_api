import random
import time

from models_app.models import User
from models_app.models import Alarm


def generate_data():
    print("Начало генерации данных")
    data = []
    count = random.randint(5, 15)

    user = User.objects.first()
    if not user:
        return

    for _ in range(count):
        data.append(Alarm(
            speed=random.randint(200, 1000),  # Скорость (в км/x),
            magnetic=random.uniform(0.01, 5.0),  # МП - магнитное поле (float),
            scatter_area=random.uniform(2000, 15000),  # ЭПР - эффективное площадь рассеяния (метры кубические) (float),
            user_id=user.id
        ))

    Alarm.objects.bulk_create(data)
    print("Генерация данных завершена")

    time_delay = random.randint(1, 5)
    time.sleep(time_delay * 60)

    return generate_data()
