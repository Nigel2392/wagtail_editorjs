from typing import Any
from django.test import TestCase
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from bs4 import BeautifulSoup

from .utils import BaseEditorJSTest
from ..editorjs.element import EditorJSElement
from ..render import render_editorjs_html
from ..registry import (
    EditorJSTune,
    EditorJSFeature,
    InlineEditorJSFeature,
    EDITOR_JS_FEATURES,
)


class TestEditorJSTune(EditorJSTune):
    allowed_attributes = {
        "*": ["data-testing-id"],
    }

    def tune_element(self, element: EditorJSElement, tune_value: Any, context=None) -> EditorJSElement:
        element.attrs["data-testing-id"] = tune_value
        return element


# Create your tests here.
class TestEditorJSFeatures(BaseEditorJSTest):

    def setUp(self) -> None:
        super().setUp()
        self.tune = TestEditorJSTune(
            "test_tune_feature",
            None
        )
        EDITOR_JS_FEATURES.register(
            "test_tune_feature",
            self.tune,
        )

    def test_editorjs_features(self):

        html = []
        test_data = []
        for i, feature in enumerate(EDITOR_JS_FEATURES.features.values()):
            test_data_list = feature.get_test_data()
            if not isinstance(feature, (EditorJSFeature))\
                or not test_data_list:
                continue

            for j, data in enumerate(test_data_list):
                test_data_list[j] = {
                    "id": "test_id_{}_{}".format(i, j),
                    "type": feature.tool_name,
                    "data": data,
                    "tunes": {
                        "test_tune_feature": "test_id_{}_{}_tune".format(i, j)
                    }
                }
                
            test_data.extend(test_data_list)

            for data in test_data_list:
                if hasattr(feature, "render_block_data"):
                    tpl = feature.render_block_data(data)
                    tpl = self.tune.tune_element(tpl, data["tunes"]["test_tune_feature"])                    
                    html.append(tpl)

        rendered_1 = render_editorjs_html(
            EDITOR_JS_FEATURES.keys(),
            {"blocks": test_data},
            clean=False,
        )

        rendered_2 = render_to_string(
            "wagtail_editorjs/rich_text.html",
            {"html": mark_safe("\n".join([str(h) for h in html]))}
        )

        soup1 = BeautifulSoup(rendered_1, "html.parser")
        soup2 = BeautifulSoup(rendered_2, "html.parser")

        self.assertHTMLEqual(soup1.decode(False), soup2.decode(False))

    def test_cleaned_editorjs_features(self):

        html = []
        test_data = []
        for i, feature in enumerate(EDITOR_JS_FEATURES.features.values()):
            test_data_list = feature.get_test_data()
            if not isinstance(feature, (EditorJSFeature))\
                or not test_data_list:
                continue

            for j, data in enumerate(test_data_list):
                test_data_list[j] = {
                    "id": "test_id_{}_{}".format(i, j),
                    "type": feature.tool_name,
                    "data": data,
                    "tunes": {
                        "test_tune_feature": "test_id_{}_{}_tune".format(i, j)
                    }
                }

            for data in test_data_list:
                if hasattr(feature, "render_block_data"):
                    tpl = feature.render_block_data(data)
                    tpl = self.tune.tune_element(tpl, data["tunes"]["test_tune_feature"])
                    html.append(tpl)

            test_data.extend(test_data_list)

        rendered = render_editorjs_html(
            EDITOR_JS_FEATURES.keys(),
            {"blocks": test_data},
            clean=True,
        )

        soup = BeautifulSoup(rendered, "html.parser")

        for data in test_data:
            block = soup.find(attrs={"data-testing-id": data["tunes"]["test_tune_feature"]})

            feature = EDITOR_JS_FEATURES[data["type"]]
            element = feature.render_block_data(data)
            element = self.tune.tune_element(element, data["tunes"]["test_tune_feature"])

            soup_element = BeautifulSoup(str(element), "html.parser")

            self.assertHTMLEqual(str(block).replace("\n", "").strip(), str(soup_element).replace("\n", "").strip())


