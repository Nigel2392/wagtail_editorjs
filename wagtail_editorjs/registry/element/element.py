from typing import Any, Union, TypeVar
from .attrs import EditorJSElementAttribute
from .utils import add_attributes, wrap_tag, _make_attr
import bs4


ElementType = TypeVar("ElementType", bound="EditorJSElement")


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

    @property
    def is_wrapped(self):
        return False

    def __setitem__(self, key, value):
        if "key" in self.attrs:
            attrs = self.attrs[key]
            attrs.append(value)
            self.attrs[key] = attrs
        else:
            self.attrs[key] = _make_attr(value)

    def add_attributes(self, **attrs: Union[str, list[str], dict[str, Any]]):
        return add_attributes(self, **attrs)
    
    @property
    def content(self):
        if isinstance(self._content, list):
            return "\n".join([str(item) for item in self._content])
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
    

class EditorJSSoupElement(EditorJSElement):
    def __init__(self, raw_html: str):
        self.raw_html = raw_html
        self.soup = bs4.BeautifulSoup(raw_html, "html.parser")
        self.soupContent = self.soup.contents[0]

    @property
    def content(self):
        return str(self.soup)
    
    @content.setter
    def content(self, value):
        self.soup = bs4.BeautifulSoup(value, "html.parser")
        self.soupContent = self.soup.contents[0]

    @property
    def attrs(self):
        return self.soupContent.attrs            

    def __str__(self):
        return str(self.soup)
    
    def append(self, element: "EditorJSElement"):
        if isinstance(element, EditorJSSoupElement):
            self.soupContent.append(element.soup)
        elif isinstance(element, str):
            self.soupContent.append(element)
        elif isinstance(element, EditorJSElement):
            self.soupContent.append(str(element))
        else:
            raise TypeError(f"Invalid type {type(element)}")
        
    def add_attributes(self, **attrs: Union[str, list[str], dict[str, Any]]):
        for key, value in attrs.items():
            if key == "class_" or key == "class":
                classList = self.soupContent.get("class", [])
                if isinstance(value, str):
                    classList.append(value)
                elif isinstance(value, list):
                    classList.extend(value)
                self.soupContent["class"] = classList
            else:
                self.soupContent[key] = value


def wrapper(element: EditorJSElement, attrs: dict[str, EditorJSElementAttribute] = None, tag: str = "div"):

    if isinstance(element, EditorJSWrapper) or getattr(element, "is_wrapped", False):
        return add_attributes(element, **attrs)

    return EditorJSWrapper(element, attrs=attrs, tag=tag)


class EditorJSWrapper(EditorJSElement):
    @property
    def is_wrapped(self):
        return True
    
    @property
    def wrapped_element(self) -> Union[ElementType, list[ElementType]]:
        if len(self._content) > 1:
            return self._content

        return self._content[0]
    
    def __init__(self,
            content: Union[ElementType, list[ElementType]],
            attrs: dict[str, EditorJSElementAttribute] = None,
            close_tag: bool = True,
            tag: str = "div",
        ):
        
        if not isinstance(content, (list, tuple)):
            content = [content]

        for item in content:

            item_type = type(item)
            if item_type == EditorJSWrapper:
                raise ValueError(
                    "Cannot nest EditorJSWrapper elements\n"
                    "Please check if the element is already wrapped before re-wrapping.\n"
                )

            if not issubclass(item_type, EditorJSElement):
                raise ValueError(f"Expected EditorJSElement got {type(item)}")

        super().__init__(tag, content, attrs, close_tag)
