from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .registry import (
    EditorJSElement,
    InlineEditorJSFeature,
    EDITOR_JS_FEATURES,
)


def render_editorjs_html(features: list[str], data: dict, context=None) -> str:
    """
        Renders the editorjs widget.
    """

    if "blocks" not in data:
        data["blocks"] = []

    feature_mappings = {
        feature: EDITOR_JS_FEATURES[feature]
        for feature in features
    }

    html = []
    for block in data["blocks"]:

        feature = block["type"]
        tunes = block.get("tunes", {})
        feature_mapping = feature_mappings[feature]

        element: EditorJSElement = feature_mapping.render_block_data(block, context)

        for tune_name, tune_value in tunes.items():
            element = feature_mappings[tune_name].tune_element(element, tune_value, context)

        for inline in EDITOR_JS_FEATURES.inline_features:
            inline: InlineEditorJSFeature
            element = inline.parse_inline_data(element, block, context)

        html.append(element)

    return render_to_string("wagtail_editorjs/rich_text.html", {"html": mark_safe("".join([str(h) for h in html]))})



