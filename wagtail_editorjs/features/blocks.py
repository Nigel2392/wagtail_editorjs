from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _

import bleach

from ..registry import (
    EditorJSFeature,
    EditorJSBlock,
    EditorJSElement,
    wrap_tag,
)




class CodeFeature(EditorJSFeature):
    allowed_tags = ["code"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)

        if 'code' not in data['data']:
            raise forms.ValidationError('Invalid code value')
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("code", block["data"]["code"], attrs={"class": "code"})
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "code": "print('Hello, World!')",
            }
        ]


class DelimiterFeature(EditorJSFeature):
    allowed_tags = ["hr"]
    allowed_attributes = ["class"]

    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("hr", close_tag=False, attrs={"class": "delimiter"})
    
    @classmethod
    def get_test_data(cls):
        return [{}, {}, {}]


class HeaderFeature(EditorJSFeature):
    allowed_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)

        level = data["data"].get("level")
        if level > 6 or level < 1:
            raise forms.ValidationError("Invalid level value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement(
            "h" + str(block["data"]["level"]),
            block["data"].get("text")
        )
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "level": heading,
                "text": f"Header {heading}",
            } for heading in range(1, 7)
        ]


class HTMLFeature(EditorJSFeature):
    allowed_tags = bleach.ALLOWED_TAGS
    allowed_attributes = bleach.ALLOWED_ATTRIBUTES

    def validate(self, data: Any):
        super().validate(data)

        if "html" not in data["data"]:
            raise forms.ValidationError("Invalid html value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("div", block["data"]["html"], attrs={"class": "html"})
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "html": "<p>This is an HTML block.</p>",
            }
        ]

class WarningFeature(EditorJSFeature):
    allowed_tags = ["div", "h2", "p"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)

        if "title" not in data["data"]:
            raise forms.ValidationError("Invalid title value")
        
        if "message" not in data["data"]:
            raise forms.ValidationError("Invalid message value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement(
            "div",
            attrs={
                "class": "warning",
            },
            content=[
                EditorJSElement(
                    "h2",
                    block["data"]["title"],
                ),
                EditorJSElement(
                    "p",
                    block["data"]["message"],
                ),
            ]
        )
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "title": "Warning",
                "message": "This is a warning message.",
            }
        ]


class TableFeature(EditorJSFeature):
    allowed_tags = ["table", "tr", "th", "td", "thead", "tbody", "tfoot"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)

        if "content" not in data["data"]:
            raise forms.ValidationError("Invalid content value")
        
        if "withHeadings" not in data["data"]:
            raise forms.ValidationError("Invalid withHeadings value")

    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        table = []

        if block["data"]["withHeadings"]:
            headings = block["data"]["content"][0]
            table.append(EditorJSElement(
                "thead",
                EditorJSElement(
                    "tr",
                    [
                        EditorJSElement("th", heading)
                        for heading in headings
                    ]
                )
            ))

            content = block["data"]["content"][1:]
        else:
            content = block["data"]["content"]

        tbody = EditorJSElement("tbody")
        for row in content:
            tbody.append(
                EditorJSElement(
                    "tr",
                    [
                        EditorJSElement("td", cell)
                        for cell in row
                    ]
                )
            )

        table.append(tbody)

        return EditorJSElement("table", table)

    @classmethod
    def get_test_data(cls):
        return [
            {
                "withHeadings": False,
                "content": [
                    ["1", "2", "3"],
                    ["4", "5", "6"],
                    ["7", "8", "9"],
                ],
            },
            {
                "withHeadings": True,
                "content": [
                    ["Heading 1", "Heading 2", "Heading 3"],
                    ["1", "2", "3"],
                    ["4", "5", "6"],
                    ["7", "8", "9"],
                ],
            }
        ]


class BlockQuoteFeature(EditorJSFeature):
    allowed_tags = ["blockquote", "footer"]
    allowed_attributes = ["class"]
    
    def validate(self, data: Any):
        super().validate(data)

        if "text" not in data["data"]:
            raise forms.ValidationError("Invalid text value")
        
        if "caption" not in data["data"]:
            raise forms.ValidationError("Invalid caption value")
        
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        text = block["data"]["text"]
        caption = block["data"]["caption"]
        return EditorJSElement(
            "blockquote",
            [
                text,
                wrap_tag("footer", {}, caption),
            ],
            {
                "class": "blockquote",
            }
        )
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "text": "This is a quote.",
                "caption": "Anonymous",
            }
        ]

