from typing import Any
from wagtail import hooks

from django.urls import reverse
from django.middleware import csrf
from wagtail.models import Page
from wagtail.admin.widgets import AdminPageChooser
from wagtail.images.widgets import AdminImageChooser
from wagtail.images import get_image_model
from wagtail.documents import get_document_model

from ..hooks import (
    REGISTER_HOOK_NAME,
    BUILD_CONFIG_HOOK,
)
from ..registry import (
    EditorJSFeature,
    InlineEditorJSFeature,
    EditorJSTune,
    EditorJSFeatures,
    EditorJSElement,
    EditorJSBlock,
    wrap_tag,
)



Image = get_image_model()
Document = get_document_model()


# EDITOR_JS_EditorJSFeatureS = {
#     "attaches": EditorJSFeature("attaches", "AttachesTool", "wagtail_editorjs/vendor/tools/attaches.js"),
#     "checklist": EditorJSFeature("checklist", "Checklist", "wagtail_editorjs/vendor/tools/checklist.js"),
#     "code": EditorJSFeature("code", "CodeTool", "wagtail_editorjs/vendor/tools/code.js"),
#     "delimiter": EditorJSFeature("delimiter", "Delimiter", "wagtail_editorjs/vendor/tools/delimiter.js"),
#     "embed": EditorJSFeature("embed", "Embed", "wagtail_editorjs/vendor/tools/embed.js"),
#     "header": EditorJSFeature("header", "Header", "wagtail_editorjs/vendor/tools/header.js"),
#     "image": EditorJSFeature("image", "Image", "wagtail_editorjs/vendor/tools/image.js"),
#     "inline-code": EditorJSFeature("inline-code", "InlineCode", "wagtail_editorjs/vendor/tools/inline-code.js"),
#     "link": EditorJSFeature("link", "LinkTool", "wagtail_editorjs/vendor/tools/link.js"),
#     "wagtail-link": EditorJSFeature("wagtail-link", "WagtailLinkTool", "wagtail_editorjs/js/tools/wagtail-link.js"),
#     "marker": EditorJSFeature("marker", "Marker", "wagtail_editorjs/vendor/tools/marker.js"),
#     "nested-list": EditorJSFeature("nested-list", "NestedList", "wagtail_editorjs/vendor/tools/nested-list.js"),
#     "paragraph": EditorJSFeature("paragraph", "Paragraph", "wagtail_editorjs/vendor/tools/paragraph.umd.js"),
#     "quote": EditorJSFeature("quote", "Quote", "wagtail_editorjs/vendor/tools/quote.js"),
#     "raw": EditorJSFeature("raw", "RawTool", "wagtail_editorjs/vendor/tools/raw.js"),
#     "table": EditorJSFeature("table", "Table", "wagtail_editorjs/vendor/tools/table.js"),
#     "warning": EditorJSFeature("warning", "Warning", "wagtail_editorjs/vendor/tools/warning.js"),
#     "textAlignmentTune": EditorJSFeature("textAlignmentTune", "AlignmentBlockTune", "wagtail_editorjs/vendor/tools/text-alignment.js"),
# }


class NestedListElement(EditorJSElement):
    def __init__(self, tag: str, items: list[EditorJSElement], close_tag: bool = True, attrs: dict[str, Any] = None):
        super().__init__(tag=tag, content=None, close_tag=close_tag, attrs=attrs)
        self.items = items

    def __str__(self):
        return wrap_tag(self.tag, self.attrs, "".join([str(item) for item in self.items]), self.close_tag)

    def append(self, item: "NestedListElement"):
        self.items.append(item)


def parse_list(items: list[dict[str, Any]], element: str) -> NestedListElement:
    s = []

    for item in items:
        content = item.get("content")
        items = item.get("items")
        s.append(f"<li>{content}\n")
        if items:
            s.append(parse_list(items, element))
        s.append(f"</li>")

    return NestedListElement(element, s)

class NestedListFeature(EditorJSFeature):
    def validate(self, data: Any):
        super().validate(data)

        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
        
        items = data["data"].get("items")
        if not items:
            raise ValueError("Invalid items value")
        
        if "style" not in data["data"]:
            raise ValueError("Invalid style value")
        
        if data["data"]["style"] not in ["ordered", "unordered"]:
            raise ValueError("Invalid style value")
    
    def render_block_data(self, block: EditorJSBlock) -> EditorJSElement:
        element = "ol" if block["data"]["style"] == "ordered" else "ul"
        return parse_list(block["data"]["items"], element)

class CheckListFeature(EditorJSFeature):
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
    
    def render_block_data(self, block: EditorJSBlock) -> EditorJSElement:
        s = []
        for item in block["data"]["items"]:
            class_ = "checklist-item"
            if item["checked"]:
                class_ += " checked"

            s.append(wrap_tag("li", {"class": class_}, item["text"]))

        return EditorJSElement("ul", "\n\t".join(s))

class HeaderFeature(EditorJSFeature):
    def validate(self, data: Any):
        super().validate(data)

        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
        
        level = data["data"].get("level")
        if level > 6 or level < 1:
            raise ValueError("Invalid level value")
    
    def render_block_data(self, block: EditorJSBlock) -> EditorJSElement:
        return EditorJSElement(
            "h" + str(block["data"]["level"]),
            block["data"].get("text")
        )

class LinkFeature(InlineEditorJSFeature):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tag_name="a", **kwargs)
        self.must_have_attrs = {
            "class": "wagtail-link",
            "data-id": None,
            "data-parent-id": None,
            "href": None,
        }

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["pageChooserId"] =\
            f"editorjs-page-chooser-{context['widget']['attrs']['id']}"
        return config


    def render_template(self, context: dict[str, Any] = None):
        return AdminPageChooser().render_html(
            f"editorjs-page-chooser-{context['widget']['attrs']['id']}",
            None,
            {"id": f"editorjs-page-chooser-{context['widget']['attrs']['id']}"}
        )
    

    def build_element(self, soup, element: EditorJSElement, matches: dict[str, Any], block_data):
        super().build_element(soup, element, matches, block_data)
        for item, attrs in matches.items():
            

            pageId = attrs["data-id"]
            parentId = attrs["data-parent-id"]
            page = Page.objects.get(id=pageId)

            # delete all attributes
            for key in list(item.attrs.keys()):
                del item[key]

            item["href"] = page.get_url()
            item["data-parent-id"] = parentId
            item["data-id"] = pageId

class ImageFeature(EditorJSFeature):
    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["imageChooserId"] =\
            f"editorjs-image-chooser-{context['widget']['attrs']['id']}"
        config["config"]["getImageUrl"] = reverse("wagtail_editorjs:image_for_id_fmt")
        return config

    def validate(self, data: Any):
        super().validate(data)

        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
        
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
    
    def render_block_data(self, block: EditorJSBlock) -> EditorJSElement:
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

        attrs = {}
        if classlist:
            attrs["class"] = classlist

        if styles:
            attrs["style"] = styles

        
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
                    "src": image.file.url,
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
                "src": image.file.url,
                "alt": block["data"].get("alt"),
                **attrs,
            },
        )


class TableFeature(EditorJSFeature):
    def validate(self, data: Any):
        super().validate(data)

        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
        
        if "content" not in data["data"]:
            raise ValueError("Invalid content value")
        
        if "withHeadings" not in data["data"]:
            raise ValueError("Invalid withHeadings value")

    def render_block_data(self, block: EditorJSBlock) -> EditorJSElement:
        table = []
        for i, row in enumerate(block["data"]["content"]):
            tr = []
            for cell in row:
                tag = "th" if block["data"]["withHeadings"] and i == 0 else "td"
                tr.append(wrap_tag(tag, {}, cell))
            table.append(wrap_tag("tr", {}, "".join(tr)))

        return EditorJSElement("table", "".join(table))


class AttachesFeature(EditorJSFeature):

    def validate(self, data: Any):
        super().validate(data)

        if "file" not in data:
            raise ValueError("Invalid file value")
        
        if "id" not in data["file"]:
            raise ValueError("Invalid id value")
        
        if "title" not in data["file"]:
            raise ValueError("Invalid title value")
        
        if "url" not in data["file"]:
            raise ValueError("Invalid url value")

    def render_block_data(self, block: EditorJSBlock) -> EditorJSElement:

        document_id = block["data"]["file"]["id"]
        document = Document.objects.get(id=document_id)

        return EditorJSElement(
            "a",
            block["data"]["file"]["title"],
            close_tag=True,
            attrs={
                "href": document.url,
                "data-id": block["data"]["file"]["id"],
            },
        )

class AlignmentBlockTune(EditorJSTune):
    def validate(self, data: Any):
        super().validate(data)
        alignment = data.get("alignment")
        if alignment not in ["left", "center", "right"]:
            raise ValueError("Invalid alignment value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any) -> EditorJSElement:
        element = super().tune_element(element, tune_value)
        element.add_attributes(class_=f"align-content-{tune_value['alignment'].strip()}")
        return element


class TextVariantTune(EditorJSTune):
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
        
    def tune_element(self, element: EditorJSElement, tune_value: Any) -> EditorJSElement:
        element = super().tune_element(element, tune_value)
        element.add_attributes(class_=tune_value)
        return element

@hooks.register(BUILD_CONFIG_HOOK)
def build_editorjs_config(widget, context, config):
    config["minHeight"] = 30


@hooks.register(REGISTER_HOOK_NAME)
def register_editor_js_features(registry: EditorJSFeatures):

    registry.register(
        "attaches",
        AttachesFeature(
            "attaches",
            "CSRFAttachesTool",
            js=[
                "wagtail_editorjs/vendor/tools/attaches.js",
                "wagtail_editorjs/js/tools/attaches.js",
            ],
            inlineToolbar = True,
            config={
                "endpoint": reverse("wagtail_editorjs:attaches_upload"),
            },
        ),
    )
    registry.register(
        "checklist",
        CheckListFeature(
            "checklist",
            "Checklist",
            "wagtail_editorjs/vendor/tools/checklist.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "code",
        EditorJSFeature(
            "code",
            "CodeTool",
            "wagtail_editorjs/vendor/tools/code.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "delimiter",
        EditorJSFeature(
            "delimiter",
            "Delimiter",
            "wagtail_editorjs/vendor/tools/delimiter.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "embed",
        EditorJSFeature(
            "embed",
            "Embed",
            "wagtail_editorjs/vendor/tools/embed.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "header",
        HeaderFeature(
            "header",
            "Header",
            "wagtail_editorjs/vendor/tools/header.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "image",
        ImageFeature(
            "image",
            "WagtailImageTool",
            js = [
                "wagtail_editorjs/js/tools/wagtail-image.js",
            ],
            config={},
        ),
    )
    registry.register(
        "inline-code",
        EditorJSFeature(
            "inline-code",
            "InlineCode",
            js = [
                "wagtail_editorjs/vendor/tools/inline-code.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "marker",
        EditorJSFeature(
            "marker",
            "Marker",
            js = [
                "wagtail_editorjs/vendor/tools/marker.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "nested-list",
        NestedListFeature(
            "nested-list",
            "NestedList",
            js = [
                "wagtail_editorjs/vendor/tools/nested-list.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "paragraph",
        EditorJSFeature(
            "paragraph",
            "Paragraph",
            js = [
                "wagtail_editorjs/vendor/tools/paragraph.umd.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "quote",
        EditorJSFeature(
            "quote",
            "Quote",
            js = [
                "wagtail_editorjs/vendor/tools/quote.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "raw",
        EditorJSFeature(
            "raw",
            "RawTool",
            js = [
                "wagtail_editorjs/vendor/tools/raw.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "table",
        TableFeature(
            "table",
            "Table",
            js = [
                "wagtail_editorjs/vendor/tools/table.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "underline",
        EditorJSFeature(
            "underline",
            "Underline",
            js = [
                "wagtail_editorjs/vendor/tools/underline.js",
            ],
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "warning",
        EditorJSFeature(
            "warning",
            "Warning",
            js = [
                "wagtail_editorjs/vendor/tools/warning.js",
            ],
            inlineToolbar = True,
        
        ),
    )

    # Wagtail specific
    registry.register(
        "link",
        LinkFeature(
            "link",
            "WagtailLinkTool",
            js = [
                "wagtail_editorjs/js/tools/wagtail-link.js",
            ],
            inlineToolbar = True,
        
        ),
    )


    # Tunes
    registry.register(
        "text-alignment-tune",
        AlignmentBlockTune(
            "text-alignment-tune",
            "AlignmentBlockTune",
            js = [
                "wagtail_editorjs/vendor/tools/text-alignment.js",
            ],
            inlineToolbar = True,
            config={
                "default": "left",
            },
        ),
    )
    registry.register(
        "text-variant-tune",
        TextVariantTune(
            "text-variant-tune",
            "TextVariantTune",
            js = [
                "wagtail_editorjs/vendor/tools/text-variant-tune.js",
            ],
            inlineToolbar = True,
        ),
    )

    registry.register_tune("text-alignment-tune")
    registry.register_tune("text-variant-tune")

