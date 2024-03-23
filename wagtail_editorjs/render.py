from typing import Any
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

    inlines = [
        feature
        for feature in feature_mappings.values()
        if isinstance(feature, InlineEditorJSFeature)
    ]

    html = []
    inline_matches = {}
    for block in data["blocks"]:

        feature: str = block["type"]
        tunes: dict[str, Any] = block.get("tunes", {})
        feature_mapping = feature_mappings[feature]

        # Build the actual block.
        element: EditorJSElement = feature_mapping.render_block_data(block, context)

        # Tune the element.
        for tune_name, tune_value in tunes.items():
            element = feature_mappings[tune_name].tune_element(element, tune_value, context)

        for inline in inlines:
            # Parse the inline data.
            # Gather all data nescessary for building elements.
            # This data is passed in bulk to the build_elements method.
            # This allows for more efficient building of elements by limiting
            # database queries and other expensive operations.
            inline: InlineEditorJSFeature
            ret = inline.parse_inline_data(element, block, context)
            if not ret:
                continue

            soup, element, matches, d = ret
            
            if matches:
                inline_matches.setdefault(inline, [])\
                    .append((soup, element, matches, d))

        html.append(element)

    # Build all inlines.
    for inline, data in inline_matches.items():
        inline.build_elements(data, context)

    return render_to_string("wagtail_editorjs/rich_text.html", {"html": mark_safe("".join([str(h) for h in html]))})



