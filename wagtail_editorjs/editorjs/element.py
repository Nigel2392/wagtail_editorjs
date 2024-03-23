from typing import Any, Union
from .attrs import EditorJSElementAttribute
from .utils import add_attributes, wrap_tag, _make_attr


class EditorJSElement:
    """
        Base class for all elements.
    """
    
    def __init__(self, tag: str, content: Union[str, list[str]] = None, attrs: dict[str, EditorJSElementAttribute] = None, close_tag: bool = True):
        attrs = attrs or {}
        content = content or []

        if not isinstance(attrs, EditorJSElementAttribute):
            attrs = {
                key: _make_attr(value)
                for key, value in attrs.items()
            }

        if isinstance(content, str):
            content = [content]
                
        self.tag = tag
        self._content = content
        self.attrs = attrs
        self.close_tag = close_tag

    def add_attributes(self, **attrs: Union[str, list[str], dict[str, Any]]):
        return add_attributes(self, **attrs)
    
    @property
    def content(self):
        if isinstance(self._content, list):
            return "".join([str(item) for item in self._content])
        return str(self._content)
    
    @content.setter
    def content(self, value):
        if isinstance(value, list):
            self._content = value
        else:
            self._content = [value]
    
    def append(self, element: "EditorJSElement"):
        self._content.append(element)

    def __str__(self):
        return wrap_tag(
            self.tag,
            attrs = self.attrs,
            content = self.content,
            close_tag = self.close_tag
        )
