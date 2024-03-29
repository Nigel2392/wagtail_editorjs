from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _

from ..registry import (
    EditorJSTune,
    EditorJSElement,
    EditorJSWrapper,
    wrapper,
)


class AlignmentBlockTune(EditorJSTune):
    allowed_attributes = {
        "*": ["class"],
    }
    klass = "AlignmentBlockTune"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/text-alignment.js",
    ]

    def validate(self, data: Any):
        super().validate(data)
        alignment = data.get("alignment")
        if alignment not in ["left", "center", "right"]:
            raise forms.ValidationError("Invalid alignment value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)
        element.add_attributes(class_=f"align-content-{tune_value['alignment'].strip()}")
        return element


class TextVariantTune(EditorJSTune):
    allowed_tags = ["div"]
    allowed_attributes = ["class"]
    klass = "TextVariantTune"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/text-variant-tune.js",
    ]

    def validate(self, data: Any):
        super().validate(data)
        if not data:
            return
        
        if data not in [
                "call-out",
                "citation",
                "details",
            ]:
            raise forms.ValidationError("Invalid text variant value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)

        if not tune_value:
            return element
        
        if element.is_wrapped:
            element["class"] = f"text-variant-{tune_value}"

        return EditorJSElement(
            "div",
            element,
            attrs={"class": f"text-variant-{tune_value}"},
        )


class ColorTune(EditorJSTune):
    allowed_attributes = {
        "*": ["class", "style"],
    }
    js = [
        "wagtail_editorjs/js/tools/wagtail-color-tune.js",
    ]
    klass = "WagtailTextColorTune"

    def validate(self, data: Any):
        super().validate(data)
        if not data:
            return
        
        if not isinstance(data, dict):
            raise forms.ValidationError("Invalid color value")
        
        if "color" not in data:
            # Dont do anything
            return
        
        if not isinstance(data["color"], str):
            raise forms.ValidationError("Invalid color value")
        
        if not data["color"].startswith("#"):
            raise forms.ValidationError("Invalid color value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:
        if "color" not in tune_value:
            return element
        
        return wrapper(
            element,
            attrs={
                "class": "wagtail-editorjs-color-tuned",
                "style": {
                    "--text-color": tune_value["color"],
                },
            },
        )

class BackgroundColorTune(ColorTune):
    klass = "WagtailBackgroundColorTune"

    def tune_element(self, element: EditorJSElement, tune_value: Any, context = None) -> EditorJSElement:

        if "color" not in tune_value:
            return element
                
        classname = [
            "wagtail-editorjs-color-tuned",
        ]

        attrs = {
            "class": classname,
            "style": {
                "--background-color": tune_value["color"],
            },
        }

        if tune_value.get("stretched", None):
            attrs["class"] = classname + ["bg-stretched"]
        
        return wrapper(
            element,
            attrs=attrs,
        )
