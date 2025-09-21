import uuid

from django.contrib.auth import login

from models_app.models import User


class ForceLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.user = User.objects.first()

    def __call__(self, request):
        if not self.user:
            self.user = User.objects.create_user(username=uuid.uuid4())
        if not request.user.is_authenticated or request.user.pk != self.user.pk:
            login(request, self.user)
        return self.get_response(request)
