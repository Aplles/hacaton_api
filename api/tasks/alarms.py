import random
import time

from django.db.models import Avg
from django.db.models.signals import post_save

from api import meshnode
from api.serializers.alarms import AlarmGetSerializer
from models_app.models import Alarm, User
from models_app.models.default_alarm_conf.models import DefaultAlarmConf

left_top_lat = 56.901328
left_top_lon = 35.756830
right_bottom_lat = 56.804210
right_bottom_lon = 36.080000


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
                user_id=user.code,
                latitude=random.uniform(left_top_lat, right_bottom_lat),
                longitude=random.uniform(left_top_lon, right_bottom_lon),
            )
        )

    alarms = Alarm.objects.bulk_create(data)
    for alarm in alarms:
        post_save.send(sender=Alarm, instance=alarm, created=True)
        node = meshnode.get_mesh_node()

        print("Отправка данных другим участникам сети")
        node.send_to_nodes(
            {
                "type": "create_alarm",
                "from": node.name,
                "info": AlarmGetSerializer(alarm).data,
            }
        )
    print("Генерация данных завершена")

    time_delay = random.randint(1, 1)
    time.sleep(time_delay * 20)

    return generate_data()


def calculate_default_alarm_conf(user_code):
    print("Агрегация настроек по умолчанию")
    personal_alarms = Alarm.objects.filter(user_id=user_code).annotate(
        speed_avg=Avg("speed"),
        magnetic_avg=Avg("magnetic"),
        scatter_area_avg=Avg("scatter_area"),
    )

    personal_alarm = personal_alarms.first()

    if personal_alarm:
        DefaultAlarmConf.objects.update(
            speed=personal_alarm.speed_avg or 600,
            magnetic=personal_alarm.magnetic_avg or 2.6,
            scatter_area=personal_alarm.scatter_area_avg or 8500,
        )
        print("Агрегация завершена")

    time_delay = random.randint(10, 15)
    time.sleep(time_delay * 60)

    return calculate_default_alarm_conf(user_code)
