from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _
from ..registry import (
    EditorJSFeature,
    EditorJSBlock,
    EditorJSElement,
    wrap_tag,
)


class NestedListElement(EditorJSElement):
    def __init__(self, tag: str, items: list[EditorJSElement], close_tag: bool = True, attrs: dict[str, Any] = None):
        super().__init__(tag=tag, content=None, close_tag=close_tag, attrs=attrs)
        self.items = items

    def __str__(self):
        return wrap_tag(self.tag, self.attrs, "".join([str(item) for item in self.items]), self.close_tag)
    
    @property
    def content(self):
        return "".join([str(item) for item in self.items])
    
    @content.setter
    def content(self, value):
        if isinstance(value, list):
            self.items = value
        else:
            self.items = [value]

    def append(self, item: "NestedListElement"):
        self.items.append(item)


def parse_list(items: list[dict[str, Any]], element: str, depth = 0) -> NestedListElement:
    s = []

    for item in items:
        content = item.get("content")
        items = item.get("items")
        s.append(f"<li>{content}")
        if items:
            s.append(parse_list(items, element, depth + 1))
        s.append(f"</li>")

    return NestedListElement(element, s, attrs={"class": "nested-list", "style": f"--depth: {depth}"})

class NestedListFeature(EditorJSFeature):
    allowed_tags = ["ul", "ol", "li"]
    allowed_attributes = ["class", "style"]

    def validate(self, data: Any):
        super().validate(data)

        items = data["data"].get("items")
        if not items:
            raise forms.ValidationError("Invalid items value")
        
        if "style" not in data["data"]:
            raise forms.ValidationError("Invalid style value")
        
        if data["data"]["style"] not in ["ordered", "unordered"]:
            raise forms.ValidationError("Invalid style value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        element = "ol" if block["data"]["style"] == "ordered" else "ul"
        return parse_list(block["data"]["items"], element)

    @classmethod
    def get_test_data(cls):
        return [
            {
                "style": "unordered",
                "items": [
                    {
                        "content": "Item 1",
                        "items": [
                            {
                                "content": "Item 1.1",
                                "items": [
                                    {
                                        "content": "Item 1.1.1",
                                        "items": [],
                                    },
                                    {
                                        "content": "Item 1.1.2",
                                        "items": [],
                                    },
                                ],
                            },
                            {
                                "content": "Item 1.2",
                                "items": [],
                            },
                        ],
                    },
                    {
                        "content": "Item 2",
                        "items": [],
                    },
                ],
            },
        ]


class CheckListFeature(EditorJSFeature):
    allowed_tags = ["ul", "li"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)
        
        items = data["data"].get("items")
        if not items:
            raise forms.ValidationError("Invalid items value")
        
        for item in items:
            if "checked" not in item:
                raise forms.ValidationError("Invalid checked value")
            
            if "text" not in item:
                raise forms.ValidationError("Invalid text value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        s = []
        for item in block["data"]["items"]:
            class_ = "checklist-item"
            if item["checked"]:
                class_ += " checked"

            s.append(wrap_tag("li", {"class": class_}, item["text"]))

        return EditorJSElement("ul", "".join(s), attrs={"class": "checklist"})
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "items": [
                    {
                        "checked": True,
                        "text": "Item 1",
                    },
                    {
                        "checked": False,
                        "text": "Item 2",
                    },
                ],
            }
        ]

