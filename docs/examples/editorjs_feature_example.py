

from typing import Any
from django import forms
from wagtail_editorjs.hooks import REGISTER_HOOK_NAME
from wagtail_editorjs.registry import (
    EditorJSFeature, EditorJSFeatures,
    EditorJSElement, EditorJSBlock,
)
from wagtail import hooks


class CustomImageFeature(EditorJSFeature):
    # These tags are allowed and will not be cleaned by bleach if enabled.
    allowed_tags = ["img"]
    allowed_attributes = ["src", "alt", "style"]

    # Provide extra configuration for the feature.
    def get_config(self, context: dict[str, Any]):
        # This context is always present.
        # It is the widget context - NOT the request context.
        config = super().get_config() or {}
        config["config"] = {} # my custom configuration
        return config
    
    def validate(self, data: Any):
        super().validate(data)

        if 'url' not in data['data']:
            raise forms.ValidationError('Invalid data.url value')

        if "caption" not in data["data"]:
            raise forms.ValidationError('Invalid data.caption value')
        
    # ...
        
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        # Context is not guaranteed to be present. This is the request context.
        return EditorJSElement(
            "img",
            close_tag=False,
            attrs={
                "src": block["data"]["url"],
                "alt": block["data"]["caption"],
                "style": {
                    "border": "1px solid black" if block["data"]["withBorder"] else "none",
                    "background-color": "lightgray" if block["data"]["withBackground"] else "none",
                    "width": "100%" if block["data"]["stretched"] else "auto",
                }
            },
        )
    

@hooks.register(REGISTER_HOOK_NAME)
def register_editorjs_features(features: EditorJSFeatures):
    # The feature name as you'd like to use in your field/block.
    feature_name = "simple-image"

    # The classname as defined in javascript.
    # This is accessed with `window.[feature_js_class]`.
    # In this case; `window.SimpleImage`.
    feature_js_class = "SimpleImage"

    # Register the feature with the editor.
    features.register(
        feature_name,
        CustomImageFeature(
            feature_name,
            feature_js_class,
            js = [
                # Import from CDN
                "https://cdn.jsdelivr.net/npm/@editorjs/simple-image",
            ],
        ),
    )
