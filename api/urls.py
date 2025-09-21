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
        peer_ids=["d9d7708b-62ec-4d8d-8ee6-19e0114a8678"]
    )
    return Response(str(data))


urlpatterns = [
    path('main/', main)
]
