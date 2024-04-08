from typing import Any
from django import forms
from wagtail_editorjs.hooks import REGISTER_HOOK_NAME
from wagtail_editorjs.registry import EditorJSFeatures, EditorJSTune, EditorJSElement
from wagtail import hooks


class AlignmentBlockTune(EditorJSTune):
    allowed_attributes = {"*": ["class"]}
    klass = "AlignmentBlockTune"
    js = ["https://cdn.jsdelivr.net/npm/editorjs-text-alignment-blocktune@latest"]

    def validate(self, data: Any):
        super().validate(data)
        alignment = data.get("alignment")
        if alignment not in ["left", "center", "right"]:
            raise forms.ValidationError("Invalid alignment value")
        
    def tune_element(self, element: EditorJSElement, tune_value: Any, context=None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)
        element.add_attributes(class_=f"align-content-{tune_value['alignment'].strip()}")
        return element
    
@hooks.register(REGISTER_HOOK_NAME)
def register_editor_js_features(registry: EditorJSFeatures):
    registry.register(
        "text-alignment-tune",
        AlignmentBlockTune(
            "text-alignment-tune",
            inlineToolbar=True,
            config={
                "default": "left",
            },
        ),
    )
  
    # To apply globally to all features
    registry.register_tune("text-alignment-tune")
  
    # Or optionally for a specific feature remove the wildcard above
    # and use the following (given the features "header" and "paragraph" are used in the editor)
    # registry.register_tune("text-alignment-tune", "header")
    # registry.register_tune("text-alignment-tune", "paragraph")
