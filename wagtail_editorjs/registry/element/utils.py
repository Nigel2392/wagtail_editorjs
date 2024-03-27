from typing import Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .element import EditorJSElement

from .attrs import (
    EditorJSElementAttribute,
    EditorJSStyleAttribute,
)


def make_attrs(attrs: dict[str, Any]) -> str:

    attrs = {
        key: _make_attr(value)
        for key, value in attrs.items()
    }

    return " ".join([f'{key}="{value}"' for key, value in attrs.items()])


def wrap_tag(tag_name, attrs, content = None, close_tag = True):
    attrs = attrs or {}
    attributes = f" {make_attrs(attrs)}" if attrs else ""
    if content is None and close_tag:
        return f"<{tag_name}{attributes}></{tag_name}>"
    elif content is None and not close_tag:
        return f"<{tag_name}{attributes}>"
    return f"<{tag_name}{attributes}>{content}</{tag_name}>"


def add_attributes(element: "EditorJSElement", **attrs: Union[str, list[str], dict[str, Any]]):
    """
        Adds attributes to the element.
    """
    for key, value in attrs.items():
        if key.endswith("_"):
            key = key[:-1]

        if key in element.attrs:
            element.attrs[key].extend(value)
        else:
            element.attrs[key] = _make_attr(value)
    
    return element


def _make_attr(value: Union[str, list[str], dict[str, Any]]):

    if isinstance(value, EditorJSElementAttribute):
        return value

    if isinstance(value, dict):
        return EditorJSStyleAttribute(value)

    return EditorJSElementAttribute(value)
