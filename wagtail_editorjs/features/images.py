from typing import Any, TYPE_CHECKING
from django import forms
from django.urls import reverse, path
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.http import (
    HttpRequest,
    FileResponse,
    HttpResponse,
)

from wagtail.images.widgets import AdminImageChooser
from wagtail.images import get_image_model
from wagtail.images.models import SourceImageIOError

if TYPE_CHECKING:
    from wagtail.images.models import Image as AbstractImage


from ..registry import (
    EditorJSFeature,
    EditorJSBlock,
    EditorJSElement,
    FeatureViewMixin,
    wrapper,
)

Image = get_image_model()


class BaseImageFeature(FeatureViewMixin, EditorJSFeature):

    def get_urlpatterns(self):
        return [
            path(
                f"{self.tool_name}/",
                self.handler,
                name=f"{self.tool_name}_for_id_fmt",
            ),
            path(
                f"{self.tool_name}/<int:image_id>/",
                self.handler,
                name=self.tool_name,
            )
        ]

    def handle_get(self, request: HttpRequest, image_id: int) -> "AbstractImage":
        image: "AbstractImage" = get_object_or_404(Image, pk=image_id)

        # Get/generate the rendition
        try:
            rendition = image.get_rendition("original")
        except SourceImageIOError:
            return HttpResponse(
                "Source image file not found", content_type="text/plain", status=410
            )

        with rendition.get_willow_image() as willow_image:
            mime_type = willow_image.mime_type

        # Serve the file
        f = rendition.file.open("rb")
        response = FileResponse(f, filename=image.filename, content_type=mime_type)
        response["Content-Length"] = f.size
        return response


class ImageFeature(BaseImageFeature):
    allowed_tags = ["img", "figure", "figcaption"]
    allowed_attributes = {
        "img": ["src", "alt", "class", "style"],
        "figure": ["class", "style"],
        "figcaption": ["class"],
    }
    klass = "WagtailImageTool"
    js = [
        "wagtail_editorjs/js/tools/wagtail-image.js",
    ]

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["imageChooserId"] =\
            f"editorjs-image-chooser-{context['widget']['attrs']['id']}"
        config["config"]["getImageUrl"] = reverse(f"wagtail_editorjs:{self.tool_name}_for_id_fmt")
        return config

    def validate(self, data: Any):
        super().validate(data)

        d = data["data"]
        if "imageId" not in d:
            raise forms.ValidationError("Invalid imageId value")
            
        
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
                
        imgTag = EditorJSElement(
            "img",
            close_tag=False,
            attrs={
                "src": url,
                "alt": block["data"].get("alt"),
            },
        )

        if block["data"].get("usingCaption"):
            caption = block["data"].get("alt")
            w = EditorJSElement(
                "figure",
                close_tag=True,
            )
            figcaption = EditorJSElement(
                "figcaption",
                caption,
            )
            w.append(imgTag)
            w.append(figcaption)
        else:
            w = imgTag

        return wrapper(w, attrs=attrs)
    
    @classmethod
    def get_test_data(cls):
        instance = Image.objects.first()
        return [
            {
                "imageId": instance.pk,
                "withBorder": True,
                "stretched": False,
                "backgroundColor": "#000000",
                "usingCaption": False,
                "alt": "Image",
                "caption": "Image",
            },
            {
                "imageId": instance.pk,
                "withBorder": False,
                "stretched": True,
                "backgroundColor": None,
                "usingCaption": True,
                "alt": "Image",
                "caption": "Image",
            }
        ]


class ImageRowFeature(BaseImageFeature):
    allowed_tags = ["div", "img"]
    allowed_attributes = ["class", "style"]
    klass = "ImageRowTool"
    js = [
        "wagtail_editorjs/js/tools/wagtail-image-row.js",
    ]

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["imageChooserId"] =\
            f"editorjs-images-chooser-{context['widget']['attrs']['id']}"
        config["config"]["getImageUrl"] = reverse(f"wagtail_editorjs:{self.tool_name}_for_id_fmt")
        return config
    
    def render_template(self, context: dict[str, Any] = None):
        widget_id = f"editorjs-images-chooser-{context['widget']['attrs']['id']}"
        return AdminImageChooser().render_html(
            widget_id,
            None,
            {"id": widget_id}
        )

    def validate(self, data: Any):
        super().validate(data)

        if "images" not in data["data"]:
            raise forms.ValidationError("Invalid images value")
        
        if not data["data"]["images"]:
            raise forms.ValidationError("Invalid images value")
        
        if "settings" not in data["data"] or data["data"]["settings"] is None:
            raise forms.ValidationError("Invalid settings value")
        
        for image in data["data"]["images"]:
            if "id" not in image:
                raise forms.ValidationError("Invalid id value")
            
            if "title" not in image:
                raise forms.ValidationError("Invalid title value")
    
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


        return wrapper(
            EditorJSElement("div", s, attrs={
                "class": "image-row",
            }),
            attrs={
                "class": "stretched"
            } if block["data"]["settings"].get("stretched") else {}
        )

    @classmethod
    def get_test_data(cls):
        images = Image.objects.all()[0:3]
        return [
            {
                "images": [
                    {
                        "id": image.pk,
                        "title": image.title,
                    } for image in images
                ],
                "settings": {
                    "stretched": True,
                },
            }
        ]
