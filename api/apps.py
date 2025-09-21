import os
import threading
import uuid

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return
        from models_app.models import User
        from models_app.models.default_alarm_conf.models import DefaultAlarmConf

        from . import meshnode

        current_user = User.objects.first()
        default_alarm_conf = DefaultAlarmConf.objects.first()
        if not current_user:
            current_user = User.objects.create_user(username=uuid.uuid4())

        if not default_alarm_conf:
            DefaultAlarmConf.objects.create(
                speed=1,
                magnetic=1.0,
                scatter_area=1.0,
                speed_weight=1.0,
                magnetic_weight=1.0,
                scatter_weight=1.0,
            )

        from api.tasks import generate_data

        def mesh_starter():
            node = meshnode.start_mesh_node(current_user.code)
            if node:
                print("[MESH] MeshNode стартовала!")

        def generate_alarm_data_starter():
            generate_data()

        threading.Thread(target=mesh_starter, daemon=True).start()
        threading.Thread(target=generate_alarm_data_starter, daemon=True).start()
