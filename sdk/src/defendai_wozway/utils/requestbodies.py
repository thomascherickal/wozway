

import io
from dataclasses import dataclass
import re
from typing import (
    Any,
    Optional,
)

from .forms import serialize_form_data, serialize_multipart_form

from .serializers import marshal_json

SERIALIZATION_METHOD_TO_CONTENT_TYPE = {
    "json": "application/json",
    "form": "application/x-www-form-urlencoded",
    "multipart": "multipart/form-data",
    "raw": "application/octet-stream",
    "string": "text/plain",
}


@dataclass
class SerializedRequestBody:
    media_type: str
    content: Optional[Any] = None
    data: Optional[Any] = None
    files: Optional[Any] = None


def serialize_request_body(
    request_body: Any,
    nullable: bool,
    optional: bool,
    serialization_method: str,
    request_body_type,
) -> Optional[SerializedRequestBody]:
    if request_body is None:
        if not nullable and optional:
            return None

    media_type = SERIALIZATION_METHOD_TO_CONTENT_TYPE[serialization_method]

    serialized_request_body = SerializedRequestBody(media_type)

    if re.match(r"(application|text)\/.*?\+*json.*", media_type) is not None:
        serialized_request_body.content = marshal_json(request_body, request_body_type)
    elif re.match(r"multipart\/.*", media_type) is not None:
        (
            serialized_request_body.media_type,
            serialized_request_body.data,
            serialized_request_body.files,
        ) = serialize_multipart_form(media_type, request_body)
    elif re.match(r"application\/x-www-form-urlencoded.*", media_type) is not None:
        serialized_request_body.data = serialize_form_data(request_body)
    elif isinstance(request_body, (bytes, bytearray, io.BytesIO, io.BufferedReader)):
        serialized_request_body.content = request_body
    elif isinstance(request_body, str):
        serialized_request_body.content = request_body
    else:
        raise TypeError(
            f"invalid request body type {type(request_body)} for mediaType {media_type}"
        )

    return serialized_request_body
