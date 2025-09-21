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
        from models_app.models.user_alarm_conf.models import UserAlarmConf

        from . import meshnode
        from django.core.management import call_command

        call_command('migrate', interactive=False, run_syncdb=True)

        current_user = User.objects.first()
        default_alarm_conf = DefaultAlarmConf.objects.first()
        user_alarm_conf = UserAlarmConf.objects.first()

        if not current_user:
            current_user = User.objects.create_user(username=uuid.uuid4())

        if not default_alarm_conf:
            DefaultAlarmConf.objects.create(
                speed=600,
                magnetic=2.6,
                scatter_area=8500,
                speed_weight=2.0,
                magnetic_weight=3.0,
                scatter_weight=2.5,
            )

        if not user_alarm_conf:
            UserAlarmConf.objects.create()

        from api.tasks import calculate_default_alarm_conf, generate_data

        def mesh_starter():
            node = meshnode.start_mesh_node(current_user.code)
            if node:
                print("[MESH] MeshNode стартовала!")

            threading.Thread(target=generate_data, daemon=True).start()
            threading.Thread(target=calculate_default_alarm_conf, daemon=True, args=(current_user.code,)).start()

        threading.Thread(target=mesh_starter, daemon=True).start()
