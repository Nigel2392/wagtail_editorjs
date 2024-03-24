from wagtail import hooks
from django.urls import reverse

from ..hooks import (
    REGISTER_HOOK_NAME,
    BUILD_CONFIG_HOOK,
)
from ..registry import (
    EditorJSFeature,
    EditorJSFeatures,
    EditorJSJavascriptFeature,
)
from ..editorjs.features import (
    AttachesFeature,
    BlockQuoteFeature,
    CheckListFeature,
    CodeFeature,
    DelimiterFeature,
    WarningFeature,
    HeaderFeature,
    HTMLFeature,
    ImageFeature,
    LinkFeature,
    NestedListFeature,
    TableFeature,
    AlignmentBlockTune,
    TextVariantTune,
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
            "CSRFAttachesTool",
            js=[
                "wagtail_editorjs/vendor/tools/attaches.js",
                "wagtail_editorjs/js/tools/attaches.js",
            ],
            config={
                "endpoint": reverse("wagtail_editorjs:attaches_upload"),
            },
        ),
    )
    registry.register(
        "checklist",
        CheckListFeature(
            "checklist",
            "Checklist",
            "wagtail_editorjs/vendor/tools/checklist.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "code",
        CodeFeature(
            "code",
            "CodeTool",
            "wagtail_editorjs/vendor/tools/code.js",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "delimiter",
        DelimiterFeature(
            "delimiter",
            "Delimiter",
            "wagtail_editorjs/vendor/tools/delimiter.js",
            inlineToolbar = True,
        ),
    )
    registry.register(
        "header",
        HeaderFeature(
            "header",
            "Header",
            "wagtail_editorjs/vendor/tools/header.js",
            inlineToolbar = True,
        
        ),
    )
    registry.register(
        "image",
        ImageFeature(
            "image",
            "WagtailImageTool",
            js = [
                "wagtail_editorjs/js/tools/wagtail-image.js",
            ],
            config={},
        ),
    )
    registry.register(
        "inline-code",
        EditorJSFeature(
            "inline-code",
            "InlineCode",
            js = [
                "wagtail_editorjs/vendor/tools/inline-code.js",
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
                "wagtail_editorjs/vendor/tools/marker.js",
            ],
            inlineToolbar = True,
            allowed_tags=["mark"],
        ),
    )
    registry.register(
        "nested-list",
        NestedListFeature(
            "nested-list",
            "NestedList",
            js = [
                "wagtail_editorjs/vendor/tools/nested-list.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "paragraph",
        EditorJSFeature(
            "paragraph",
            "Paragraph",
            js = [
                "wagtail_editorjs/vendor/tools/paragraph.umd.js",
            ],
            inlineToolbar = True,
            allowed_tags=["p"],
        ),
    )
    registry.register(
        "quote",
        BlockQuoteFeature(
            "quote",
            "Quote",
            js = [
                "wagtail_editorjs/vendor/tools/quote.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "raw",
        HTMLFeature(
            "raw",
            "RawTool",
            js = [
                "wagtail_editorjs/vendor/tools/raw.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "table",
        TableFeature(
            "table",
            "Table",
            js = [
                "wagtail_editorjs/vendor/tools/table.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "underline",
        EditorJSFeature(
            "underline",
            "Underline",
            js = [
                "wagtail_editorjs/vendor/tools/underline.js",
            ],
            inlineToolbar = True,
        ),
    )
    registry.register(
        "warning",
        WarningFeature(
            "warning",
            "Warning",
            js = [
                "wagtail_editorjs/vendor/tools/warning.js",
            ],
            inlineToolbar = True,
        ),
    )

    # Wagtail specific
    registry.register(
        "link",
        LinkFeature(
            "link",
            "WagtailLinkTool",
            js = [
                "wagtail_editorjs/js/tools/wagtail-link.js",
            ],
            inlineToolbar = True,
        ),
    )


    # Tunes
    registry.register(
        "text-alignment-tune",
        AlignmentBlockTune(
            "text-alignment-tune",
            "AlignmentBlockTune",
            js = [
                "wagtail_editorjs/vendor/tools/text-alignment.js",
            ],
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
            "TextVariantTune",
            js = [
                "wagtail_editorjs/vendor/tools/text-variant-tune.js",
            ],
            inlineToolbar = True,
        ),
    )

    # Register initializers
    registry.register(
        "undo-redo",
        EditorJSJavascriptFeature(
            "undo-redo",
            js = [
                "wagtail_editorjs/vendor/tools/undo-redo.js",
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
                "wagtail_editorjs/vendor/tools/drag-drop.js",
                "wagtail_editorjs/js/init/drag-drop.js",
            ],
            weight=1,
        ),
    )

    # Add tunes
    registry.register_tune("text-alignment-tune")
    registry.register_tune("text-variant-tune")

