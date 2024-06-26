from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.templatetags.static import static
from django.utils.safestring import mark_safe

import bleach

from ..registry import (
    PageChooserURLsMixin,
    EditorJSFeature,
    EditorJSBlock,
    EditorJSElement,
    EditorJSSoupElement,
    wrap_tag,
)



class CodeFeature(EditorJSFeature):
    allowed_tags = ["code"]
    allowed_attributes = ["class"]
    klass="CodeTool"
    js=[
        "wagtail_editorjs/vendor/editorjs/tools/code.js",
    ]

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
    klass="Delimiter"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/delimiter.js",
    ]

    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("hr", close_tag=False, attrs={"class": "delimiter"})
    
    @classmethod
    def get_test_data(cls):
        return [{}, {}, {}]


class HeaderFeature(EditorJSFeature):
    allowed_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
    allowed_attributes = ["class"]
    klass="Header"
    js=[
        "wagtail_editorjs/vendor/editorjs/tools/header.js",
    ]

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
    klass="RawTool"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/raw.js",
    ]

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
                "html": "<p>This is a HTML block.</p>",
            }
        ]

class WarningFeature(EditorJSFeature):
    allowed_tags = ["div", "h2", "p"]
    allowed_attributes = ["class"]
    klass="Warning"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/warning.js",
    ]

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
    klass="Table"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/table.js",
    ]

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
    klass="Quote"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/quote.js",
    ]

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

from wagtail import blocks


class EditorJSFeatureStructBlock(blocks.StructBlock):
    MUTABLE_META_ATTRIBUTES = blocks.StructBlock.MUTABLE_META_ATTRIBUTES + [
        "allowed_tags", "allowed_attributes"
    ]

    def __init__(self, *args, allowed_tags: list[str] = None, allowed_attributes: dict[str, list[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_meta_options({
            "allowed_tags": allowed_tags,
            "allowed_attributes": allowed_attributes,
        })

        for _, block in self.child_blocks.items():
            if isinstance(block, (blocks.StreamBlock, blocks.ListBlock)):
                raise ValueError("StreamBlock and ListBlock are not allowed in StructBlock children for the EditorJSFeatureStructBlock")

def get_allowed_tags(instance: EditorJSFeatureStructBlock, block: blocks.Block, l = None) -> list[str]:

    if hasattr(block, "allowed_tags"):
        l = block.allowed_tags
    elif hasattr(block.meta, "allowed_tags"):
        l = block.meta.allowed_tags

    l = l or []

    if isinstance(block, blocks.StructBlock):
        for _, b in block.child_blocks.items():
            l += get_allowed_tags(instance, b, l)

    return list(set(list(l) + ["div"]))

def get_allowed_attributes(instance: EditorJSFeatureStructBlock, block: blocks.Block, d = None) -> dict[str, list[str]]:
    if hasattr(block, "allowed_attributes"):
        obj_dict = block.allowed_attributes
    elif hasattr(block.meta, "allowed_attributes"):
        obj_dict = block.meta.allowed_attributes
    else:
        obj_dict = {}

    if d is None:
        d = obj_dict
    else:
        for key, value in obj_dict.items():
            d[key] = set(list(d.get(key, [])) + list(value))
    
    if isinstance(d, list) and "class" not in d:
        d.append("class")
    elif isinstance(d, dict):
        v = d.get("div", [])
        if isinstance(v, list) and "class" not in v:
            v.append("class")
        elif isinstance(v, set) and "class" not in v:
            v.add("class")
        elif isinstance(v, str):
            v = set(v.split(" "))
            v.add("class")

        d["div"] = v

    if isinstance(block, blocks.StructBlock):
        for _, b in block.child_blocks.items():
            d = get_allowed_attributes(instance, b, d)

    return d


class WagtailBlockFeature(EditorJSFeature):
    def __init__(self, 
            tool_name: str,
            block: blocks.Block,
            klass: str = None,
            config: dict = None,
            weight: int = 0, # Weight is used to manage which features.js files are loaded first.
            allowed_tags: list[str] = None,
            allowed_attributes: dict[str, list[str]] = None,
            **kwargs
        ):

        if not isinstance(block, blocks.Block) and issubclass(block, blocks.Block):
            block = block()


        self.block = block

        self.block.set_name(
            self.block.__class__.__name__.lower()
        )

        super().__init__(
            tool_name, klass, None, None, None, config, weight, allowed_tags, allowed_attributes, **kwargs
        )

    def init_static(self, css, js):
        pass

    def init_attrs(self, allowed_tags, allowed_attributes):
        pass

    @cached_property
    def widget(self):
        return blocks.BlockWidget(self.block)

    def get_config(self, context: dict[str, Any] = None) -> dict:
        data = super().get_config(context)
        config = data.get("config", {})
        config["rendered"] = self.widget.render_with_errors(
            "__PREFIX__", self.block.get_default(),
        )
        data["config"] = config
        return data
    
    
    @cached_property
    def allowed_tags(self):
        return get_allowed_tags(self, self.block)

    @cached_property
    def allowed_attributes(self):
        return get_allowed_attributes(self, self.block)
    
    @property
    def js(self):
        return [
            *self.widget.media._js,
            mark_safe(f"<script src=\"{ static('wagtail_editorjs/js/tools/wagtail-block.js') }\" data-name=\"{ self.block.name }\" data-title=\"{ self.block.label }\"></script>"),
        ]
    
    def validate(self, data: Any):
        super().validate(data)

        if "block" not in data["data"]:
            raise forms.ValidationError("Invalid block value")
        
        try:
            data["data"]["block"] = self.block.get_prep_value(
                self.block.clean(self.block.to_python(data["data"]["block"]))
            )
        except blocks.StreamBlockValidationError as e:
            raise e
        except blocks.list_block.ListBlockValidationError as e:
            raise e
        except blocks.struct_block.StructBlockValidationError as e:
            raise e
        except Exception as e:
            raise e
        
    def value_for_form(self, value: dict) -> dict:
        value = super().value_for_form(value)
        value["data"]["block"] = self.block.get_form_state(
            self.block.to_python(value["data"]["block"])
        )
        return value
    
    def render_block_data(self, block: EditorJSBlock, context=None) -> EditorJSElement:
        value: blocks.StructValue = self.block.to_python(block["data"]["block"])
        return EditorJSSoupElement(f"<div class=\"{self.tool_name}\">{ self.block.render(value) }</div>")
    
    @classmethod
    def get_test_data(cls):
        return []
    
    @property
    def css(self):
        return self.widget.media._css
        
    @property
    def klass(self):
        return f"WagtailBlockTool_{ self.block.name }"

    @js.setter
    def js(self, data: Any): pass

    @css.setter
    def css(self, data: Any): pass

    @klass.setter
    def klass(self, data: Any): pass

    

from wagtail.models import Page
from wagtail.admin.widgets import AdminPageChooser


class ButtonFeature(PageChooserURLsMixin, EditorJSFeature):
    allowed_tags:       list[str]            = ["a"]
    allowed_attributes: dict[str, list[str]] = {
        "a": ["href", "class"]
    }
    chooser_class = AdminPageChooser
    model         = Page
    klass         = "PageButtonTool"
    js            = [
        "wagtail_editorjs/js/tools/wagtail-button-tool.js",
    ]

    @cached_property
    def widget(self):
        if self.chooser_class is None:
            return None
        
        return self.chooser_class()
    
    def validate(self, data: Any):
        super().validate(data)

        if "pageId" not in data["data"]:
            raise forms.ValidationError("Invalid id value")
        
        if "text" not in data["data"]:
            raise forms.ValidationError("Invalid text value")

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"][
            "chooserId"
        ] = f"editorjs-{self.model._meta.model_name}-button-chooser-{context['widget']['attrs']['id']}"
        return config
    
    def render_block_data(self, block: EditorJSBlock, context=None) -> EditorJSElement:
        try:
            page = self.model.objects.get(id=block["data"]["pageId"])
        except self.model.DoesNotExist:
            return None

        request = None
        if context:
            request = context.get("request")

        anchor = EditorJSElement(
            "a",
            block["data"]["text"],
            {
                "href": page.get_url(request),
                "class": "editor-button",
            }
        )

        return EditorJSElement(
            "div", anchor, {"class": "editor-button-container"},
        )

    def render_template(self, context: dict[str, Any] = None):
        if not self.widget:
            return super().render_template(context)
        
        return self.widget.render_html(
            f"editorjs-{self.model._meta.model_name}-button-chooser-{context['widget']['attrs']['id']}",
            None,
            {
                "id": f"editorjs-{self.model._meta.model_name}-button-chooser-{context['widget']['attrs']['id']}"
            },
        )

    @classmethod
    def get_test_data(cls):
        pages = cls.model.objects.all()[:5]

        return [
            {
                "pageId": page.id,
                "text": page.title,
            }
            for page in pages
        ]

