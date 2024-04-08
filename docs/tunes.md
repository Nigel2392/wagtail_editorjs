# Integrating Text Alignment Tune in EditorJS

Let's walk through the process of adding a text alignment tune to EditorJS. This tune allows content creators to align text within blocks. We'll break down the implementation into digestible steps, explaining the purpose and functionality of each method involved.

## Step 1: Import Required Modules

Start by importing the necessary Python classes and modules. This setup involves Django for form validation, typing for type annotations, and specific classes from Wagtail and the EditorJS integration:

```python
from typing import Any
from django import forms
from wagtail_editorjs.hooks import REGISTER_HOOK_NAME
from wagtail_editorjs.registry import EditorJSFeature, EditorJSFeatures, EditorJSTune, EditorJSElement
from wagtail import hooks
```

## Step 2: Define the `AlignmentBlockTune` Class

This class is the core of our tune, extending `EditorJSTune` to add text alignment functionality:

```python
class AlignmentBlockTune(EditorJSTune):
    allowed_attributes = {"*": ["class"]}
    klass = "AlignmentBlockTune"
    js = ["https://cdn.jsdelivr.net/npm/editorjs-text-alignment-blocktune@latest"]
```

### The `validate` Method

This method ensures the provided alignment value is valid. It checks if the alignment value is one of the accepted options: left, center, or right. If not, it raises a form validation error:

```python
    def validate(self, data: Any):
        super().validate(data)
        alignment = data.get("alignment")
        if alignment not in ["left", "center", "right"]:
            raise forms.ValidationError("Invalid alignment value")
```

### The `tune_element` Method

This method applies the alignment tune to an element. It adjusts the class attribute of the element to include the specified alignment, dynamically adding styling to align content as desired:

```python
    def tune_element(self, element: EditorJSElement, tune_value: Any, context=None) -> EditorJSElement:
        element = super().tune_element(element, tune_value, context=context)
        element.add_attributes(class_=f"align-content-{tune_value['alignment'].strip()}")
        return element
```

## Step 3: Register the Tune with EditorJS

Finally, we register the tune to make it available for use in EditorJS. This involves adding it to the EditorJSFeatures registry and specifying configurations like the default alignment:

```python
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

```

By following these steps, you've added a text alignment tune to EditorJS, enhancing your text blocks with alignment options. This feature not only improves the appearance of your content but also adds to the overall user experience by providing more control over text presentation.