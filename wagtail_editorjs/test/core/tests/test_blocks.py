from wagtail import blocks
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import time

from wagtail_editorjs.features import (
    WagtailBlockFeature,
)
from wagtail_editorjs.render import render_editorjs_html
from wagtail_editorjs.registry import (
    EDITOR_JS_FEATURES,
)

from .base import BaseEditorJSTest


class TestWagtailBlockFeatureBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    text = blocks.CharBlock()
    sub_block = blocks.StructBlock([
        ("sub_title", blocks.CharBlock()),
        ("sub_text", blocks.CharBlock()),
    ])

    class Meta:
        allowed_tags = ["h1", "h2", "p"]

    def render(self, value, context=None):
        return f"<h1>{value['title']}</h1><p>{value['text']}</p><h2>{value['sub_block']['sub_title']}</h2><p>{value['sub_block']['sub_text']}</p>"


class TestWagtailBlockFeature(BaseEditorJSTest):

    def setUp(self) -> None:
        super().setUp()

        self.block = TestWagtailBlockFeatureBlock()
        self.feature = WagtailBlockFeature(
            "test_feature",
            block=self.block,
        )

        EDITOR_JS_FEATURES.register(
            "test_feature",
            self.feature,
        )
        

    def test_wagtail_block_feature(self):
        test_data = {
            "test_feature-title": "Test Title",
            "test_feature-text": "Test Text",
            "test_feature-sub_block-sub_title": "Sub Title",
            "test_feature-sub_block-sub_text": "Sub Text",
        }

        feature_value = {
            "type": "test_feature",
            "data": {
                "__prefix__": "test_feature",
                "block": test_data,
            }
        }

        editorjs_value = {
            "time": int(time.time()),
            "blocks": [feature_value],
            "version": "0.0.0",
        }

        html = render_editorjs_html(features=["test_feature"], data=editorjs_value)
        feature_html = str(self.feature.render_block_data(feature_value))
        
        self.assertHTMLEqual(
            html,
            render_to_string(
                "wagtail_editorjs/rich_text.html",
                {"html": mark_safe(feature_html)}
            ),
        )

        self.assertInHTML(
            "<h1>Test Title</h1>",
            feature_html,
        )

        self.assertInHTML(
            "<p>Test Text</p>",
            feature_html,
        )

        self.assertInHTML(
            "<h2>Sub Title</h2>",
            feature_html,
        )

        self.assertInHTML(
            "<p>Sub Text</p>",
            feature_html,
        )

