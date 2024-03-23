from .registry import (
    EditorJSElement,
    EditorJSFeature,
    InlineEditorJSFeature,
    EditorJSTune,
    EDITOR_JS_FEATURES,
)



def render_editorjs_html(features: list[str], data: dict, context=None) -> str:
    """
        Renders the editorjs widget.
    """

    if "blocks" not in data:
        data["blocks"] = []

    html = []
    features_mapping = {
        feature: EDITOR_JS_FEATURES[feature]
        for feature in features
    }

    for block in data["blocks"]:

        feature = block["type"]
        tunes = block.get("tunes", {})
        feature_mapping = features_mapping[feature]

        element: EditorJSElement = feature_mapping.render_block_data(block)

        for tune_name, tune_value in tunes.items():
            element = features_mapping[tune_name].tune_element(element, tune_value)

        for inline in EDITOR_JS_FEATURES.inline_features:
            inline: InlineEditorJSFeature
            element = inline.parse_inline_data(element, block)

        html.append(element)

    return "\n".join([str(item) for item in html])




