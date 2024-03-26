# Add an EditorJS feature

In this section we are going to add an already defined EditorJS feature to the list of supported features.
We will add the [simple-image](https://github.com/editor-js/simple-image) feature.

First we will register the feature with our editor.
To keep things consistent; we can import the hook name from `wagtail_editorjs.hooks`.
Let's import everything first.

```python
from typing import Any
from django import forms
from wagtail_editorjs.hooks import REGISTER_HOOK_NAME
from wagtail_editorjs.registry import (
    EditorJSFeature, EditorJSFeatures,
    EditorJSElement, EditorJSBlock,
)
from wagtail import hooks
```

We can now get started creating the feature itself.
As seen from the data-format in the github package, the feature requires the following fields:
- `url`: The URL of the image.
- `caption`: The caption of the image.
- `withBorder`: A boolean value to determine if the image should have a border.
- `withBackground`: A boolean value to determine if the image should have a background.
- `stretched`: A boolean value to determine if the image should be stretched.

We will create a new class `CustomImageFeature` that extends `EditorJSFeature`.
For now we will only override the `validate` method.

We will also set the required attributes for cleaning.
```python
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

        ...
```

Next we can override the `render_block_data` method.
This method is used to render the block for display to the user on the frontend.
```python
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
```

We also provide a way to easily test this feature.
All registered features are tested automatically if their `get_test_data` method returns data.
```python
    @classmethod
    def get_test_data(cls):
        return [
            {
            "url": "https://www.example.com/image.jpg",
            "caption": "Example image",
            "withBorder": True,
            "withBackground": True,
            "stretched": True,
            },
        ]
```

We can now register the feature with the editor.
The feature will be imported from a CDN provided on the package README.

```python

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
```

If you now paste a URL with an image in the editor, you should see the image rendered with the caption.
