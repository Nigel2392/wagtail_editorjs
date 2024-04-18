from typing import Any
from wagtail import hooks
from django.urls import reverse_lazy

from ..hooks import (
    REGISTER_HOOK_NAME,
    BUILD_CONFIG_HOOK,
)
from ..registry import (
    EditorJSFeature,
    EditorJSFeatures,
    EditorJSJavascriptFeature,
)
from ..features import (
    AttachesFeature,
    BlockQuoteFeature,
    CheckListFeature,
    CodeFeature,
    DelimiterFeature,
    WarningFeature,
    HeaderFeature,
    HTMLFeature,
    ImageFeature,
    ImageRowFeature,
    ButtonFeature,
    LinkFeature,
    LinkAutoCompleteFeature,
    DocumentFeature,
    NestedListFeature,
    TableFeature,
    AlignmentBlockTune,
    TextVariantTune,
    BackgroundColorTune,
    ColorTune,
)

@hooks.register(BUILD_CONFIG_HOOK)
def build_editorjs_config(widget, context, config):
    config["minHeight"] = 150


@hooks.register(REGISTER_HOOK_NAME)
def register_editor_js_features(registry: EditorJSFeatures):

    registry.register(
        "attaches",
        AttachesFeature(
            "attaches",
        ),
    )
    registry.register(
        "checklist",
        CheckListFeature(
            "checklist",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "code",
        CodeFeature(
            "code",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "delimiter",
        DelimiterFeature(
            "delimiter",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "header",
        HeaderFeature(
            "header",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "inline-code",
        EditorJSFeature(
            "inline-code",
            "InlineCode",
            js = [
                "wagtail_editorjs/vendor/editorjs/tools/inline-code.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "marker",
        EditorJSFeature(
            "marker",
            "Marker",
            js = [
                "wagtail_editorjs/vendor/editorjs/tools/marker.js",
            ],
            inlineToolbar = True,
            allowed_tags=["mark"],
        ),
    )
    registry.register(
        "nested-list",
        NestedListFeature(
            "nested-list",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "paragraph",
        EditorJSFeature(
            "paragraph",
            "Paragraph",
            js = [
                "wagtail_editorjs/vendor/editorjs/tools/paragraph.umd.js",
            ],
            inlineToolbar = True,
            allowed_tags=["p"],
        ),
    )
    registry.register(
        "quote",
        BlockQuoteFeature(
            "quote",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "raw",
        HTMLFeature(
            "raw",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "table",
        TableFeature(
            "table",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "underline",
        EditorJSFeature(
            "underline",
            "Underline",
            js = [
                "wagtail_editorjs/vendor/editorjs/tools/underline.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "warning",
        WarningFeature(
            "warning",
            inlineToolbar = True,
        ),
    )
    
    registry.register(
        "link-autocomplete",
        LinkAutoCompleteFeature(
            "link-autocomplete",
        ),
    )

    # Wagtail specific
    registry.register(
        "button",
        ButtonFeature(
            "button",
        )
    )
    registry.register(
        "link",
        LinkFeature(
            "link",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "image",
        ImageFeature(
            "image",
        ),
    )
    registry.register(
        "images",
        ImageRowFeature(
            "images",
        ),
    )
    registry.register(
        "document",
        DocumentFeature(
            "document",
            config={},
            inlineToolbar = True,
        ),
    )

    # Tunes
    registry.register(
        "text-alignment-tune",
        AlignmentBlockTune(
            "text-alignment-tune",
            inlineToolbar = True,
            config={
                "default": "left",
            },
        ),
    )
    registry.register(
        "text-variant-tune",
        TextVariantTune(
            "text-variant-tune",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "background-color-tune",
        BackgroundColorTune(
            "background-color-tune",
            config={
                "defaultStretched": True,
            }
        ),
    )
    registry.register(
        "text-color-tune",
        ColorTune(
            "text-color-tune",
        ),
    )

    # Register initializers
    registry.register(
        "undo-redo",
        EditorJSJavascriptFeature(
            "undo-redo",
            js = [
                "wagtail_editorjs/vendor/editorjs/tools/undo-redo.js",
                "wagtail_editorjs/js/init/undo-redo.js",
            ],
            weight=0,
        ),
    )

    registry.register(
        "drag-drop",
        EditorJSJavascriptFeature(
            "drag-drop",
            js = [
                "wagtail_editorjs/vendor/editorjs/tools/drag-drop.js",
                "wagtail_editorjs/js/init/drag-drop.js",
            ],
            weight=1,
        ),
    )

    disallows_tunes = [
        "images",
        "raw",
    ]

    allows_color_tunes = [
        "attaches",
    ]

    for feature in registry.features.values():
        if feature.tool_name in disallows_tunes:
            continue
        

    # Add tunes
        registry.register_tune("text-alignment-tune", feature.tool_name)
        registry.register_tune("text-variant-tune", feature.tool_name)

        if feature.tool_name in allows_color_tunes or not feature.tool_name in disallows_tunes:
            registry.register_tune("background-color-tune", feature.tool_name)
            registry.register_tune("text-color-tune", feature.tool_name)


# 
# from django.contrib.auth import get_user_model
# from wagtail.snippets.widgets import AdminSnippetChooser
# from wagtail_editorjs.hooks import REGISTER_HOOK_NAME
# from wagtail_editorjs.registry import (
#     EditorJSFeatures,
#     ModelInlineEditorJSFeature,
# )
# 
# 
# class InlineUserChooserFeature(ModelInlineEditorJSFeature):
#     model = get_user_model()
#     chooser_class = AdminSnippetChooser
#     must_have_attrs = {
#         "data-email": None,
#     }
# 
#     @classmethod
#     def get_url(cls, instance):
#         return f"mailto:{instance.email}"
#     
#     @classmethod
#     def get_full_url(cls, instance, request):
#         return cls.get_url(instance)
# 
# 
# @hooks.register(REGISTER_HOOK_NAME)
# def register_editor_js_features(registry: EditorJSFeatures):
#     registry.register(
#         "inline-user",
#         InlineUserChooserFeature(
#             "inline-user",
#             "InlineUserTool",
#             js=[
#                 "wagtail_editorjs/js/tools/inline-user.js",
#             ],
#             config={},
#         ),
#     )
# 