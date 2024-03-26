from typing import Any

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from wagtail.models import Page
from wagtail.admin.widgets import AdminPageChooser
from wagtail.images.widgets import AdminImageChooser
from wagtail.documents.widgets import AdminDocumentChooser
from wagtail.images import get_image_model
from wagtail.documents import get_document_model

import bleach

from .utils import wrap_tag
from ..registry import (
    EditorJSFeature,
    ModelInlineEditorJSFeature,
    EditorJSTune,
    EditorJSElement,
    EditorJSBlock,
)

BYTE_SIZE_STEPS = [_("Bytes"), _("Kilobytes"), _("Megabytes"), _("Gigabytes"), _("Terabytes")]

def filesize_to_human_readable(size: int) -> str:
    for unit in BYTE_SIZE_STEPS:
        if size < 1024:
            break
        size /= 1024
    return f"{size:.0f} {unit}"



Image = get_image_model()
Document = get_document_model()


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
            raise ValueError("Invalid items value")
        
        if "style" not in data["data"]:
            raise ValueError("Invalid style value")
        
        if data["data"]["style"] not in ["ordered", "unordered"]:
            raise ValueError("Invalid style value")
    
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
            raise ValueError("Invalid items value")
        
        for item in items:
            if "checked" not in item:
                raise ValueError("Invalid checked value")
            
            if "text" not in item:
                raise ValueError("Invalid text value")
    
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

class CodeFeature(EditorJSFeature):
    allowed_tags = ["code"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)

        if 'code' not in data['data']:
            raise ValueError('Invalid code value')
    
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
            raise ValueError("Invalid level value")
    
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
            raise ValueError("Invalid html value")
    
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
            raise ValueError("Invalid title value")
        
        if "message" not in data["data"]:
            raise ValueError("Invalid message value")
    
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


class LinkFeature(ModelInlineEditorJSFeature):
    allowed_tags = ["a"]
    allowed_attributes = ["class", "href", "data-id"]
    chooser_class = AdminPageChooser
    model = Page

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_have_attrs = self.must_have_attrs | {
            "data-parent-id": None,
            "href": None,
        }


class DocumentFeature(ModelInlineEditorJSFeature):
    allowed_tags = ["a"]
    allowed_attributes = ["class", "href", "data-id"]
    chooser_class = AdminDocumentChooser
    model = Document


class ImageFeature(EditorJSFeature):
    allowed_tags = ["img", "figure", "figcaption"]
    allowed_attributes = {
        "img": ["src", "alt", "class", "style"],
        "figure": ["class", "style"],
        "figcaption": ["class"],
    }

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["imageChooserId"] =\
            f"editorjs-image-chooser-{context['widget']['attrs']['id']}"
        config["config"]["getImageUrl"] = reverse("wagtail_editorjs:image_for_id_fmt")
        return config

    def validate(self, data: Any):
        super().validate(data)

        d = data["data"]
        if "imageId" not in d:
            raise ValueError("Invalid imageId value")
            
        
    def render_template(self, context: dict[str, Any] = None):
        widget_id = f"editorjs-image-chooser-{context['widget']['attrs']['id']}"
        return AdminImageChooser().render_html(
            widget_id,
            None,
            {"id": widget_id}
        )
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        image = block["data"].get("imageId")
        image = Image.objects.get(id=image)

        classlist = []
        styles = {}
        if block["data"].get("withBorder"):
            classlist.append("with-border")

        if block["data"].get("stretched"):
            classlist.append("stretched")

        if block["data"].get("backgroundColor"):
            styles["background-color"] = block["data"]["backgroundColor"]
            classlist.append("with-background")

        attrs = {}
        if classlist:
            attrs["class"] = classlist

        if styles:
            attrs["style"] = styles

        url = image.file.url
        if not any([url.startswith(i) for i in ["http://", "https://", "//"]]) and context:
            request = context.get("request")
            if request:
                url = request.build_absolute_uri(url)

        # Caption last - we are wrapping the image in a figure tag
        if block["data"].get("usingCaption"):
            caption = block["data"].get("alt")
            wrapper = EditorJSElement(
                "figure",
                close_tag=True,
                attrs=attrs,
            )
            img = EditorJSElement(
                "img",
                close_tag=False,
                attrs={
                    "src": url,
                    "alt": caption,
                },
            )
            figcaption = EditorJSElement(
                "figcaption",
                caption,
            )
            wrapper.append(img)
            wrapper.append(figcaption)
            return wrapper


        return EditorJSElement(
            "img",
            block["data"].get("caption"),
            close_tag=False,
            attrs={
                "src": url,
                "alt": block["data"].get("alt"),
                **attrs,
            },
        )
    
    @classmethod
    def get_test_data(cls):
        # instance = Image.objects.first()
        return [
            # {
            #     "imageId": instance.pk,
            #     "withBorder": True,
            #     "stretched": False,
            #     "backgroundColor": "#000000",
            #     "usingCaption": False,
            #     "alt": "Image",
            #     "caption": "Image",
            # },
            # {
            #     "imageId": instance.pk,
            #     "withBorder": False,
            #     "stretched": True,
            #     "backgroundColor": None,
            #     "usingCaption": True,
            #     "alt": "Image",
            #     "caption": "Image",
            # }
        ]


class ImageRowFeature(EditorJSFeature):
    allowed_tags = ["div", "img"]
    allowed_attributes = ["class", "style"]

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["imageChooserId"] =\
            f"editorjs-image-chooser-{context['widget']['attrs']['id']}"
        config["config"]["getImageUrl"] = reverse("wagtail_editorjs:image_for_id_fmt")
        return config
    
    def render_template(self, context: dict[str, Any] = None):
        widget_id = f"editorjs-image-chooser-{context['widget']['attrs']['id']}"
        return AdminImageChooser().render_html(
            widget_id,
            None,
            {"id": widget_id}
        )

    def validate(self, data: Any):
        super().validate(data)

        if "images" not in data["data"]:
            raise ValueError("Invalid images value")
        
        if not data["data"]["images"]:
            raise ValueError("Invalid images value")
        
        if "settings" not in data["data"] or data["data"]["settings"] is None:
            raise ValueError("Invalid settings value")
        
        for image in data["data"]["images"]:
            if "id" not in image:
                raise ValueError("Invalid id value")
            
            if "title" not in image:
                raise ValueError("Invalid title value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        images = block["data"]["images"]
        ids = []
        for image in images:
            ids.append(image["id"])

        images = Image.objects.in_bulk(ids)
        s = []
        for id in ids:
            try:
                id = int(id)
            except ValueError:
                pass
            image = images[id]
            url = image.file.url
            if not any([url.startswith(i) for i in ["http://", "https://", "//"]]) and context:
                request = context.get("request")
                if request:
                    url = request.build_absolute_uri(url)

            s.append(EditorJSElement(
                "div",
                EditorJSElement(
                    "img",
                    close_tag=False,
                    attrs={
                        "src": url,
                        "alt": image.title,
                    }
                ),
                attrs={
                    "class": "image-wrapper",
                }
            ))

        classnames = [
            "image-row",
        ]

        if block["data"]["settings"].get("stretched"):
            classnames.append("stretched")

        return EditorJSElement("div", s, attrs={
            "class": classnames,
        })

    @classmethod
    def get_test_data(cls):
        return []

class TableFeature(EditorJSFeature):
    allowed_tags = ["table", "tr", "th", "td", "thead", "tbody", "tfoot"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)

        if "content" not in data["data"]:
            raise ValueError("Invalid content value")
        
        if "withHeadings" not in data["data"]:
            raise ValueError("Invalid withHeadings value")

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
            raise ValueError("Invalid text value")
        
        if "caption" not in data["data"]:
            raise ValueError("Invalid caption value")
        
    
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


class AttachesFeature(EditorJSFeature):
    allowed_tags = [
        "div", "p", "span", "a",
        "svg", "path",
    ]
    allowed_attributes = {
        "div": ["class"],
        "p": ["class"],
        "span": ["class"],
        "a": ["class", "href", "title"],
        "svg": ["xmlns", "width", "height", "fill", "class", "viewBox"],
        "path": ["d"],
    }

    def validate(self, data: Any):
        super().validate(data)

        if "file" not in data["data"]:
            raise ValueError("Invalid file value")
        
        if "id" not in data["data"]["file"] and not data["data"]["file"]["id"] and "url" not in data["data"]["file"]:
            raise ValueError("Invalid id/url value")
        
        if "title" not in data["data"]:
            raise ValueError("Invalid title value")
        
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:

        document_id = block["data"]["file"]["id"]
        document = Document.objects.get(pk=document_id)
        url = document.url

        if not any([url.startswith(i) for i in ["http://", "https://", "//"]]) and context:
            request = context.get("request")
            if request:
                url = request.build_absolute_uri(url)

        if block["data"]["title"]:
            title = block["data"]["title"]
        else:
            if document:
                title = document.title
            else:
                title = url

        return EditorJSElement(
            "div",
            [
                EditorJSElement(
                    "p",
                    EditorJSElement(
                        "a",
                        title,
                        attrs={"href": url},
                    ),
                    attrs={"class": "attaches-title"},
                ),
                EditorJSElement(
                    "span",
                    filesize_to_human_readable(document.file.size),
                    attrs={"class": "attaches-size"},
                ),
                EditorJSElement(
                    "a",
                    mark_safe("""<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-link" viewBox="0 0 16 16">
    <path d="M6.354 5.5H4a3 3 0 0 0 0 6h3a3 3 0 0 0 2.83-4H9q-.13 0-.25.031A2 2 0 0 1 7 10.5H4a2 2 0 1 1 0-4h1.535c.218-.376.495-.714.82-1z"/>
    <path d="M9 5.5a3 3 0 0 0-2.83 4h1.098A2 2 0 0 1 9 6.5h3a2 2 0 1 1 0 4h-1.535a4 4 0 0 1-.82 1H12a3 3 0 1 0 0-6z"/>
</svg>"""),
                    attrs={
                        "title": _("Download"),
                        "href": url,
                        "class": "attaches-link",
                        # "data-id": document_id,
                    },
                )
            ],
            attrs={"class": "attaches"},
        )
    
    @classmethod
    def get_test_data(cls):
        # instance = Document.objects.first()
        return [
            # {
            #     "file": {
            #         "id": instance.pk,
            #     },
            #     "title": "Document",
            # },
        ]
    
# def clean_alignment_class(value):
#     if any([i in value for i in ["align-content-left", "align-content-center", "align-content-right"]]):
#         return True
#     return False

class AlignmentBlockTune(EditorJSTune):
    allowed_attributes = {
        "*": ["class"],
    }
    # cleaner_funcs = {
    #     "*": {
    #         "class": clean_alignment_class,
    #     }
    # }
     
    def validate(self, data: Any):
        super().validate(data)
        alignment = data.get("alignment")
        if alignment not in ["left", "center", "right"]:
            raise ValueError("Invalid alignment value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)
        element.add_attributes(class_=f"align-content-{tune_value['alignment'].strip()}")
        return element
    
    # @classmethod
    # def get_test_data(cls):
        # return [
            # {
                # "alignment": "left",
            # },
            # {
                # "alignment": "center",
            # },
            # {
                # "alignment": "right",
            # },
        # ]


class TextVariantTune(EditorJSTune):
    allowed_tags = ["div"]
    allowed_attributes = ["class"]

    def validate(self, data: Any):
        super().validate(data)
        if not data:
            return
        
        if data not in [
                "call-out",
                "citation",
                "details",
            ]:
            raise ValueError("Invalid text variant value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)

        if not tune_value:
            return element

        return EditorJSElement(
            "div",
            element,
            attrs={"class": f"text-variant-{tune_value}"},
        )
    
    # @classmethod
    # def get_test_data(cls):
        # return [
            # "call-out",
            # "citation",
            # "details",
        # ]
