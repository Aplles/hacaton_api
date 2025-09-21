from rest_framework.response import Response
from rest_framework.views import APIView

from api import meshnode
from models_app.models import User


class TestView(APIView):

    def get(self, request, *args, **kwargs):
        user = User.objects.first()
        data = request.GET
        node = meshnode.get_mesh_node()
        node.send_to_nodes(
            {
                "type": "message",
                "msg": data,
                "from": node.name,
            }
        )
        return Response(str(data) + f" {user.code}")
