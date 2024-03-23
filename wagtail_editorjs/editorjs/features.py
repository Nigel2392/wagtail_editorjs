from typing import Any

from django.urls import reverse
from wagtail.models import Page
from wagtail.admin.widgets import AdminPageChooser
from wagtail.images.widgets import AdminImageChooser
from wagtail.images import get_image_model
from wagtail.documents import get_document_model

from .utils import wrap_tag
from ..registry import (
    EditorJSFeature,
    LazyInlineEditorJSFeature,
    EditorJSTune,
    EditorJSElement,
    EditorJSBlock,
)




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
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        s = []
        for item in block["data"]["items"]:
            class_ = "checklist-item"
            if item["checked"]:
                class_ += " checked"

            s.append(wrap_tag("li", {"class": class_}, item["text"]))

        return EditorJSElement("ul", "\n\t".join(s), attrs={"class": "checklist"})

class CodeFeature(EditorJSFeature):
    def validate(self, data: Any):
        super().validate(data)

        if 'code' not in data['data']:
            raise ValueError('Invalid code value')
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("code", block["data"]["code"], attrs={"class": "code"})

class DelimiterFeature(EditorJSFeature):
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("hr", close_tag=False, attrs={"class": "delimiter"})

class HeaderFeature(EditorJSFeature):
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

class HTMLFeature(EditorJSFeature):
    def validate(self, data: Any):
        super().validate(data)

        if "html" not in data["data"]:
            raise ValueError("Invalid html value")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement("div", block["data"]["html"], attrs={"class": "html"})

class WarningFeature(EditorJSFeature):
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
    
class LazyModelEditorJSFeature(LazyInlineEditorJSFeature):
    model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.must_have_attrs = self.must_have_attrs | {
            "data-id": None,
            f"data-{self.model._meta.model_name}": None,
        }

    def get_id(self, item, attrs: dict[str, Any], context: dict[str, Any] = None):
        return int(attrs["data-id"])
    
    def build_element(self, item, obj, context: dict[str, Any] = None):
        pass

    def build_elements(self, inline_data: list, context: dict[str, Any] = None) -> list:
        """
            Process the bulk data; fetch all pages in one go
            and build the elements.
        """
        super().build_elements(inline_data, context=context)
        ids = []
        element_soups = []
        for data in inline_data:
            # soup: BeautifulSoup
            # element: EditorJSElement
            # matches: dict[bs4.elementType, dict[str, Any]]
            # data: dict[str, Any] # Block data.
            soup, element, matches, data = data

            # Store element and soup for later replacement of content.
            element_soups.append((soup, element))

            # Item is bs4 tag, attrs are must_have_attrs
            for (item, attrs) in matches.items():
                id = self.get_id(item, attrs, context)
                ids.append((item, id))

                # delete all attributes
                for key in list(item.attrs.keys()):
                    del item[key]
        
        # Fetch all objects
        objects = self.model.objects.in_bulk([id for item, id in ids])
        for item, id in ids:
            self.build_element(item, objects[id], context)

        # Replace the element's content with the new soup
        for soup, element in element_soups:
            element.content = soup.prettify()



class LinkFeature(LazyModelEditorJSFeature):
    model = Page
    tag_name = "a"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tag_name=self.tag_name, **kwargs)
        self.must_have_attrs = self.must_have_attrs | {
            "class": "wagtail-link",
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
    
    def build_element(self, item, obj, context: dict[str, Any] = None):
        item["href"] = obj.get_url()
        item["class"] = "wagtail-link"



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

        if "content" not in data["data"]:
            raise ValueError("Invalid content value")
        
        if "withHeadings" not in data["data"]:
            raise ValueError("Invalid withHeadings value")

    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        table = []
        for i, row in enumerate(block["data"]["content"]):
            tr = []
            for cell in row:
                tag = "th" if block["data"]["withHeadings"] and i == 0 else "td"
                tr.append(wrap_tag(tag, {}, cell))
            table.append(wrap_tag("tr", {}, "".join(tr)))

        return EditorJSElement("table", "".join(table))


class BlockQuoteFeature(EditorJSFeature):
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


class AttachesFeature(EditorJSFeature):

    def validate(self, data: Any):
        super().validate(data)

        if "file" not in data["data"]:
            raise ValueError("Invalid file value")
        
        if "id" not in data["data"]["file"] and not data["data"]["file"]["id"] and "url" not in data["data"]["file"]:
            raise ValueError("Invalid id/url value")
        
        if "title" not in data["data"]["file"]:
            raise ValueError("Invalid title value")
        
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:

        if "id" in block["data"]["file"] and block["data"]["file"]["id"]:
            document_id = block["data"]["file"]["id"]
            document = Document.objects.get(id=document_id)
            url = document.url
        else:
            document = None
            url = block["data"]["file"]["url"]

        if block["data"]["file"]["title"]:
            title = block["data"]["file"]["title"]
        else:
            if document:
                title = document.title
            else:
                title = url

        return EditorJSElement(
            "a",
            title,
            close_tag=True,
            attrs={
                "href": url,
                "class": "attaches-link",
                # "data-id": block["data"]["file"]["id"],
            },
        )

class AlignmentBlockTune(EditorJSTune):
    def validate(self, data: Any):
        super().validate(data)
        alignment = data.get("alignment")
        if alignment not in ["left", "center", "right"]:
            raise ValueError("Invalid alignment value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)
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
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)

        if not tune_value:
            return element

        return EditorJSElement(
            "div",
            element,
            attrs={"class": f"text-variant-{tune_value}"},
        )
