import os
import threading

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return
        from . import meshnode

        def mesh_starter():
            node = meshnode.start_mesh_node()
            if node:
                print("[MESH] MeshNode стартовала!")

        threading.Thread(target=mesh_starter, daemon=True).start()
