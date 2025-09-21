from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import meshnode


@api_view(['GET'])
def main(request):
    data = request.GET
    node = meshnode.get_mesh_node()
    node.send_mesh_message({
        "type": "message",
        "msg": "Это всем!!",
        "from": node.unique_id
    })

    node.send_mesh_message(
        {
            "type": "message",
            "msg": "Только избранным",
            "from": node.unique_id
        },
        peer_ids=[]
    )
    return Response(str(data))


urlpatterns = [
    path('main/', main)
]
