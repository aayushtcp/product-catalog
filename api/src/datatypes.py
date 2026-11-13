from typing import Union
from typing_extensions import TypeAliasType

# Recursive type alias representing any valid JSON data structure.
JSONType = TypeAliasType(
    "JSONType",
    "Union[dict[str, JSONType], list[JSONType], str, int, float, bool, None]",
)
"""
JSONType is a recursive type alias that represents any valid JSON value.

It includes:
- Primitive types: null (`None`), boolean (`bool`), number (`int`, `float`), and string (`str`)
- Lists of JSON values (can be nested)
- Dictionaries with string keys and JSON values (can be nested)

This type is useful for annotating variables, request/response bodies, or configurations
that conform to the JSON specification.
"""
