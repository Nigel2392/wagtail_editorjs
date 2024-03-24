from django.test import TestCase
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .registry import (
    EDITOR_JS_FEATURES,
)
from .render import render_editorjs_html

# Create your tests here.
class TestEditorJSFeatures(TestCase):

    def test_editorjs_features(self):

        html = []
        test_data = []
        for feature in EDITOR_JS_FEATURES.features.values():
            test_data_list = feature.get_test_data()
            if test_data_list is None:
                continue

            for i, data in enumerate(test_data_list):
                test_data_list[i] = {
                    "id": "test_id",
                    "type": feature.tool_name,
                    "data": data,
                    "tunes": {}
                }
            test_data.extend(test_data_list)

            for data in test_data_list:
                if hasattr(feature, "render_block_data"):
                    tpl = feature.render_block_data(data)
                    html.append(tpl)

        rendered = render_editorjs_html(
            EDITOR_JS_FEATURES.keys(),
            {"blocks": test_data},
            clean=False,
        )

        self.assertEqual(rendered, render_to_string(
            "wagtail_editorjs/rich_text.html",
            {"html": mark_safe("\n".join([str(h) for h in html]))}
        ))


