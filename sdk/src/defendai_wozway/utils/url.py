

from decimal import Decimal
from typing import (
    Any,
    Dict,
    get_type_hints,
    List,
    Optional,
    Union,
    get_args,
    get_origin,
)
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .metadata import (
    PathParamMetadata,
    find_field_metadata,
)
from .values import (
    _get_serialized_params,
    _is_set,
    _populate_from_globals,
    _val_to_string,
)


def generate_url(
    server_url: str,
    path: str,
    path_params: Any,
    gbls: Optional[Any] = None,
) -> str:
    path_param_values: Dict[str, str] = {}

    globals_already_populated = _populate_path_params(
        path_params, gbls, path_param_values, []
    )
    if _is_set(gbls):
        _populate_path_params(gbls, None, path_param_values, globals_already_populated)

    for key, value in path_param_values.items():
        path = path.replace("{" + key + "}", value, 1)

    return remove_suffix(server_url, "/") + path


def _populate_path_params(
    path_params: Any,
    gbls: Any,
    path_param_values: Dict[str, str],
    skip_fields: List[str],
) -> List[str]:
    globals_already_populated: List[str] = []

    if not isinstance(path_params, BaseModel):
        return globals_already_populated

    path_param_fields: Dict[str, FieldInfo] = path_params.__class__.model_fields
    path_param_field_types = get_type_hints(path_params.__class__)
    for name in path_param_fields:
        if name in skip_fields:
            continue

        field = path_param_fields[name]

        param_metadata = find_field_metadata(field, PathParamMetadata)
        if param_metadata is None:
            continue

        param = getattr(path_params, name) if _is_set(path_params) else None
        param, global_found = _populate_from_globals(
            name, param, PathParamMetadata, gbls
        )
        if global_found:
            globals_already_populated.append(name)

        if not _is_set(param):
            continue

        f_name = field.alias if field.alias is not None else name
        serialization = param_metadata.serialization
        if serialization is not None:
            serialized_params = _get_serialized_params(
                param_metadata, f_name, param, path_param_field_types[name]
            )
            for key, value in serialized_params.items():
                path_param_values[key] = value
        else:
            pp_vals: List[str] = []
            if param_metadata.style == "simple":
                if isinstance(param, List):
                    for pp_val in param:
                        if not _is_set(pp_val):
                            continue
                        pp_vals.append(_val_to_string(pp_val))
                    path_param_values[f_name] = ",".join(pp_vals)
                elif isinstance(param, Dict):
                    for pp_key in param:
                        if not _is_set(param[pp_key]):
                            continue
                        if param_metadata.explode:
                            pp_vals.append(f"{pp_key}={_val_to_string(param[pp_key])}")
                        else:
                            pp_vals.append(f"{pp_key},{_val_to_string(param[pp_key])}")
                    path_param_values[f_name] = ",".join(pp_vals)
                elif not isinstance(param, (str, int, float, complex, bool, Decimal)):
                    param_fields: Dict[str, FieldInfo] = param.__class__.model_fields
                    for name in param_fields:
                        param_field = param_fields[name]

                        param_value_metadata = find_field_metadata(
                            param_field, PathParamMetadata
                        )
                        if param_value_metadata is None:
                            continue

                        param_name = (
                            param_field.alias if param_field.alias is not None else name
                        )

                        param_field_val = getattr(param, name)
                        if not _is_set(param_field_val):
                            continue
                        if param_metadata.explode:
                            pp_vals.append(
                                f"{param_name}={_val_to_string(param_field_val)}"
                            )
                        else:
                            pp_vals.append(
                                f"{param_name},{_val_to_string(param_field_val)}"
                            )
                    path_param_values[f_name] = ",".join(pp_vals)
                elif _is_set(param):
                    path_param_values[f_name] = _val_to_string(param)

    return globals_already_populated


def is_optional(field):
    return get_origin(field) is Union and type(None) in get_args(field)


def template_url(url_with_params: str, params: Dict[str, str]) -> str:
    for key, value in params.items():
        url_with_params = url_with_params.replace("{" + key + "}", value)

    return url_with_params


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[: -len(suffix)]
    return input_string
