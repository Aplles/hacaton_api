from typing import Any, Dict, Optional, Sequence, Type, TypedDict, Union

from django.utils.functional import Promise
from drf_spectacular.utils import OpenApiCallback, OpenApiExample, OpenApiParameter
from rest_framework.serializers import Serializer

_SerializerType = Union[Serializer, Type[Serializer]]
_StrOrPromise = Union[str, Promise]
_SchemaType = Dict[str, Any]


class DocsDict(TypedDict, total=False):
    """
    This class is used for the dfr_spectacular @extend_schema decorator.
    The purpose of the class is to eliminate typing errors when using 'mypy'.
    Example:
        SOME_DOCK_DICT: DocsDict = {
            "tags": ...,
            "description": ...,
            "responses": ...,
        }
    """

    operation_id: Optional[str]
    parameters: Optional[Sequence[Union[OpenApiParameter, _SerializerType]]]
    request: Any
    responses: Any
    auth: Optional[Sequence[str]]
    description: Optional[_StrOrPromise]
    summary: Optional[_StrOrPromise]
    deprecated: Optional[bool]
    tags: Optional[Sequence[str]]
    filters: Optional[bool]
    exclude: Optional[bool]
    operation: Optional[_SchemaType]
    methods: Optional[Sequence[str]]
    versions: Optional[Sequence[str]]
    examples: Optional[Sequence[OpenApiExample]]
    extensions: Optional[Dict[str, Any]]
    callbacks: Optional[Sequence[OpenApiCallback]]
    external_docs: Optional[Union[Dict[str, str], str]]
