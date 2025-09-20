import os
import threading
from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from . import meshnode
        from api.tasks import generate_data

        def mesh_starter():
            node = meshnode.start_mesh_node()
            if node:
                print("[MESH] MeshNode стартовала!")

        def generate_alarm_data_starter():
            generate_data()

        threading.Thread(target=mesh_starter, daemon=True).start()
        threading.Thread(target=generate_alarm_data_starter, daemon=True).start()
