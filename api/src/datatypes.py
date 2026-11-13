from typing_extensions import TypeAliasType

# Recursive type alias representing any valid JSON data structure.
JSONType = TypeAliasType(
    "JSONType",
    "dict[str, JSONType] | list[JSONType] | str | int | float | bool | None",
)
"""
A recursive type alias for any value that can appear in JSON.

It covers:
- Scalars: `None`, `bool`, `int`, `float`, and `str`
- Lists whose items are themselves JSON values
- Objects with string keys and JSON values

Use it to annotate parsed JSON, request/response payloads, or configuration data
that follows the JSON data model.
"""
