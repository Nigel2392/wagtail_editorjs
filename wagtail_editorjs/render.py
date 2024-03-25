from typing import Any
from collections import defaultdict
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from . import settings
from .registry import (
    EditorJSElement,
    BaseInlineEditorJSFeature,
    InlineEditorJSFeature,
    EDITOR_JS_FEATURES,
)
import bleach, bs4


class NullSanitizer:
    @staticmethod
    def sanitize_css(val):
        return val

def render_editorjs_html(features: list[str], data: dict, context=None, clean: bool = None) -> str:
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
        if isinstance(feature, BaseInlineEditorJSFeature)
    ]

    html = []
    for block in data["blocks"]:

        feature: str = block["type"]
        tunes: dict[str, Any] = block.get("tunes", {})
        feature_mapping = feature_mappings.get(feature, None)

        if not feature_mapping:
            continue

        # Build the actual block.
        element: EditorJSElement = feature_mapping.render_block_data(block, context)

        # if element.tag != "div":
        #     new = EditorJSElement("div", [element], attrs=element.attrs)
        #     element.attrs = {}
        #     element = new


        # Tune the element.
        for tune_name, tune_value in tunes.items():
            element = feature_mappings[tune_name].tune_element(element, tune_value, context)

        html.append(element)


    html = "\n".join([str(h) for h in html])

    soup = bs4.BeautifulSoup(html, "html.parser")
    if inlines:
        for inline in inlines:
            # Give inlines access to whole soup.
            # This allows for proper parsing of say; page or document links.
            inline: InlineEditorJSFeature
            inline.parse_inline_data(soup, context)

        # Re-render the soup.
        html = soup.decode(False)

    if clean or (clean is None and settings.CLEAN_HTML):
        allowed_tags = set({
            # Default inline tags.
            "i", "b", "strong", "em", "u", "s", "strike"
        })
        allowed_attributes = defaultdict(set)
        # cleaner_funcs = defaultdict(lambda: defaultdict(list))

        for feature in feature_mappings.values():
            allowed_tags.update(feature.allowed_tags)
            # for key, value in feature.cleaner_funcs.items():
            #     for name, func in value.items():
            #         cleaner_funcs[key][name].append(func)

            for key, value in feature.allowed_attributes.items():
                allowed_attributes[key].update(value)

        html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            css_sanitizer=NullSanitizer,
        )

    return render_to_string(
        "wagtail_editorjs/rich_text.html",
        {"html": mark_safe(html)}
    )



#         def parse_allowed_attributes(tag, name, value):
#             if (
#                 tag not in allowed_attributes\
#                 and tag not in cleaner_funcs\
#                 and "*" not in cleaner_funcs\
#                 and "*" not in allowed_attributes
#             ):
#                 return False
#             
#             if "*" in cleaner_funcs and name in cleaner_funcs["*"] and any(
#                 func(value) for func in cleaner_funcs["*"][name]
#             ):
#                 return True
#             
#             if tag in cleaner_funcs\
#                     and name in cleaner_funcs[tag]\
#                     and any(
#                         func(value) for func in cleaner_funcs[tag][name]
#                     ):
#                 return True
#             
#             if name in allowed_attributes[tag] or name in allowed_attributes["*"]:
#                 return True
#             
#             return False
