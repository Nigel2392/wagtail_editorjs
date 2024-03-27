from typing import Any
from django import forms
from django.utils.translation import gettext_lazy as _

from ..registry import (
    EditorJSTune,
    EditorJSElement,
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

        return EditorJSElement(
            "div",
            element,
            attrs={"class": f"text-variant-{tune_value}"},
        )

