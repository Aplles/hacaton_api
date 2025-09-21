from rest_framework.response import Response
from rest_framework.views import APIView

from api import meshnode


class TestView(APIView):

    def get(self, request, *args, **kwargs):
        node = meshnode.get_mesh_node()
        node.send_to_nodes(
            {
                "type": "message",
                "msg": request.GET,
                "from": node.name,
            }
        )
        return Response(str(request.GET) + f" {request.user.code}")
