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

class SubBlock(blocks.StructBlock):
    sub_title = blocks.CharBlock()
    sub_text = blocks.CharBlock()

    class Meta:
        allowed_tags = ["h3", "p"]
        allowed_attributes = {
            "h3": ["class"],
            "p": ["class"],
        }

class TestWagtailBlockFeatureBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle = blocks.CharBlock()
    sub_block = SubBlock()

    class Meta:
        allowed_tags = ["h1", "h2"]
        allowed_attributes = {
            "h1": ["class"],
            "h2": ["class"],
        }

    def render(self, value, context=None):
        return f"<h1 class='test1'>{value['title']}</h1><h2 class='test2'>{value['subtitle']}</h2><h3 class='test3'>{value['sub_block']['sub_title']}</h3><p class='test4'>{value['sub_block']['sub_text']}</p>"


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

    def test_value_for_form(self):
        test_data = {
            "title": "Test Title",
            "subtitle": "Test Text",
            "sub_block": {
                "sub_title": "Sub Title",
                "sub_text": "Sub Text",
            },
        }

        feature_value = {
            "type": "test_feature",
            "data": {
                "block": test_data,
            }
        }

        editorjs_value = {
            "time": int(time.time()),
            "blocks": [feature_value],
            "version": "0.0.0",
        }

        tdata_copy = test_data.copy()
        copied = editorjs_value.copy()

        data = EDITOR_JS_FEATURES.value_for_form(
            ["test_feature"],
            editorjs_value
        )

        self.assertTrue(isinstance(data, dict))
        self.assertIn("blocks", data)
        self.assertTrue(isinstance(data["blocks"], list))
        self.assertTrue(len(data["blocks"]) == 1, msg=f"Expected 1 block, got {len(data['blocks'])}")

        self.assertDictEqual(
            data,
            copied | {
                "blocks": [
                    {
                        "type": "test_feature",
                        "data": {
                            "block": tdata_copy,
                        }
                    }
                ]
            }
        )
        

    def test_wagtail_block_feature(self):
        test_data = {
            "title": "Test Title",
            "subtitle": "Test Text",
            "sub_block": {
                "sub_title": "Sub Title",
                "sub_text": "Sub Text",
            },
        }

        feature_value = {
            "type": "test_feature",
            "data": {
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
            "<h1 class='test1'>Test Title</h1>",
            feature_html,
        )

        self.assertInHTML(
            "<h2 class='test2'>Test Text</h2>",
            feature_html,
        )

        self.assertInHTML(
            "<h3 class='test3'>Sub Title</h3>",
            feature_html,
        )

        self.assertInHTML(
            "<p class='test4'>Sub Text</p>",
            feature_html,
        )

