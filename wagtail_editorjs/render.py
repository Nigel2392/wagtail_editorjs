from typing import Any, Union
from collections import defaultdict
from django.template.loader import render_to_string
from django.template.context import Context
from django.utils.safestring import mark_safe
from . import settings
from .registry import (
    EditorJSElement,
    InlineEditorJSFeature,
    EDITOR_JS_FEATURES,
)
import bleach, bs4


class NullSanitizer:
    @staticmethod
    def sanitize_css(val):
        return val

def render_editorjs_html(
        features: list[str],
        data: dict,
        context=None,
        clean: bool = None,
        whitelist_tags: list[str] = None,
        whitelist_attrs: Union[dict, list] = None
    ) -> str:
    """
        Renders the editorjs widget based on the features provided.
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
    for block in data["blocks"]:

        feature: str = block["type"]
        tunes: dict[str, Any] = block.get("tunes", {})
        feature_mapping = feature_mappings.get(feature, None)

        if not feature_mapping:
            continue

        # Build the actual block.
        element: EditorJSElement = feature_mapping.render_block_data(block, context)

        # Optionally tools can decide to not render the block.
        if element is None:
            continue

        # Tune the element.
        for tune_name, tune_value in tunes.items():
            element = feature_mappings[tune_name].tune_element(element, tune_value, context)

        # Add the block ID to each individual block.
        if settings.ADD_BLOCK_ID:
            # This can be used to link frontend to the admin area.
            element.attrs[settings.BLOCK_ID_ATTR] = block.get("id", "")
        
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

        if whitelist_tags:
            allowed_tags.update(whitelist_tags)

        if "*" in allowed_attributes:
            allowed_attributes["*"].add(settings.BLOCK_ID_ATTR)
        else:
            allowed_attributes["*"] = {settings.BLOCK_ID_ATTR}

        if whitelist_attrs:
            if isinstance(whitelist_attrs, dict):
                for key, value in whitelist_attrs.items():
                    allowed_attributes[key].update(value)
            else:
                for key in allowed_attributes:
                    allowed_attributes[key].update(whitelist_attrs)

        html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            css_sanitizer=NullSanitizer,
        )

    ctx = context or {}
    ctx["html"] = html

    if isinstance(context, Context):
        ctx = context.flatten()

    return render_to_string(
        "wagtail_editorjs/rich_text.html",
        context=ctx,
        request=ctx.get("request", None)
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
