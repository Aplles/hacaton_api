from rest_framework.authentication import BaseAuthentication

from models_app.models import User


class AlwaysUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user = User.objects.first()
        if not user:
            import uuid

            user = User.objects.create_user(username=str(uuid.uuid4()))
        return (user, None)
