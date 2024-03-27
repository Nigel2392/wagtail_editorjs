from .feature_registry import (
    EditorJSFeatures,
)
from .features import (
    BaseEditorJSFeature,
    EditorJSFeature,
    EditorJSJavascriptFeature,
    EditorJSTune,
    InlineEditorJSFeature,
    ModelInlineEditorJSFeature,
    TemplateNotSpecifiedError,
)
from .value import (
    EditorJSBlock,
    EditorJSValue,
)
from .element import (
    EditorJSElement,
    EditorJSElementAttribute,
    EditorJSStyleAttribute,
    wrap_tag,
    add_attributes,
)

def get_features(features: list[str] = None):
    if not features:
        features = list(EDITOR_JS_FEATURES.keys())

    for feature in features:
        if feature not in EDITOR_JS_FEATURES:
            raise ValueError(f"Unknown feature: {feature}")

    return features

EDITOR_JS_FEATURES = EditorJSFeatures()

