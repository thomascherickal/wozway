

from enum import Enum
from typing import Any, Optional

def get_discriminator(model: Any, fieldname: str, key: str) -> str:
    """
    Recursively search for the discriminator attribute in a model.

    Args:
        model (Any): The model to search within.
        fieldname (str): The name of the field to search for.
        key (str): The key to search for in dictionaries.

    Returns:
        str: The name of the discriminator attribute.

    Raises:
        ValueError: If the discriminator attribute is not found.
    """
    upper_fieldname = fieldname.upper()

    def get_field_discriminator(field: Any) -> Optional[str]:
        """Search for the discriminator attribute in a given field."""

        if isinstance(field, dict):
            if key in field:
                return f'{field[key]}'

        if hasattr(field, fieldname):
            attr = getattr(field, fieldname)
            if isinstance(attr, Enum):
                return f'{attr.value}'
            return f'{attr}'

        if hasattr(field, upper_fieldname):
            attr = getattr(field, upper_fieldname)
            if isinstance(attr, Enum):
                return f'{attr.value}'
            return f'{attr}'

        return None


    if isinstance(model, list):
        for field in model:
            discriminator = get_field_discriminator(field)
            if discriminator is not None:
                return discriminator

    discriminator = get_field_discriminator(model)
    if discriminator is not None:
        return discriminator

    raise ValueError(f'Could not find discriminator field {fieldname} in {model}')
