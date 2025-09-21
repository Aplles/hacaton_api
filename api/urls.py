from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import meshnode
from .views.subscribers import CreateSubscriber
from .views.user import InfoUser


@api_view(["GET"])
def main(request):
    data = request.GET
    node = meshnode.get_mesh_node()
    node.send_to_nodes(
        {
            "type": "message",
            "msg": data,
            "from": node.name,
        }
    )
    return Response(str(data) + f" {request.user.code}")


urlpatterns = [
    path("user/info/", InfoUser.as_view()),
    path("subscriber/", CreateSubscriber.as_view()),
]
