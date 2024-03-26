

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
    
    def validate(self, data: Any):
        """
        
        """
        super().validate(data)

        if 'url' not in data['data']:
            raise forms.ValidationError('Invalid data.url value')

        if "caption" not in data["data"]:
            raise forms.ValidationError('Invalid data.caption value')
        
    def render_block_data(self, block: EditorJSBlock, context = None) -> EditorJSElement:
        return EditorJSElement(
            "img",
            close_tag=False,
            attrs={
                "src": block.data["url"],
                "alt": block.data["caption"],
                "style": {
                    "border": "1px solid black" if block.data["withBorder"] else "none",
                    "background-color": "lightgray" if block.data["withBackground"] else "none",
                    "width": "100%" if block.data["stretched"] else "auto",
                }
            },
        )
    
    
@hooks.register(REGISTER_HOOK_NAME)
def register_editorjs_features(features: EditorJSFeatures):
    feature_name = "simple-image"
    feature_js_class = "SimpleImage"
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

