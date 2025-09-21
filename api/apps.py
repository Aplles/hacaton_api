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

        from . import meshnode

        current_user = User.objects.first()
        if not current_user:
            current_user = User.objects.create_user(username=uuid.uuid4())

        def mesh_starter():
            node = meshnode.start_mesh_node(current_user.code)
            if node:
                print("[MESH] MeshNode стартовала!")

        threading.Thread(target=mesh_starter, daemon=True).start()
