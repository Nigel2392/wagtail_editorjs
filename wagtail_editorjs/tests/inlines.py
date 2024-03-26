from django.test import TestCase


from .utils import BaseEditorJSTest
from ..registry import (
    InlineEditorJSFeature,
    EDITOR_JS_FEATURES,
)

import bs4



TESTING_HTML = """
<div class="editorjs">
    <div class="editorjs-block" data-type="paragraph">
        <p>Hello, World!</p>
    </div>
    <div class="editorjs-block" data-type="header">
        <h1>Header</h1>
    </div>
    <div class="editorjs-block" data-type="list" data-testing-id="TARGET">

    </div>
    <div class="editorjs-block" data-type="table">
        <table>
            <tr>
                <td>1</td>
                <td>2</td>
            </tr>
            <tr>
                <td>3</td>
                <td>4</td>
            </tr>
        </table>
    </div>
</div>
"""


class TestEditorJSInline(BaseEditorJSTest):
    def setUp(self):
        super().setUp()
        self.inlines = [
            feature
            for feature in EDITOR_JS_FEATURES.features.values()
            if isinstance(feature, InlineEditorJSFeature)
        ]

    def test_inlines(self):

        for feature in self.inlines:
            feature: InlineEditorJSFeature
            test_data = feature.get_test_data()

            if not test_data:
                continue

            soup = bs4.BeautifulSoup(TESTING_HTML, "html.parser")
            testing_block = soup.find("div", {"data-testing-id": "TARGET"})
            testing_block.clear()

            for i, (initial, _) in enumerate(test_data):
                initial_soup = bs4.BeautifulSoup(initial, "html.parser")
                initial_soup.attrs["data-testing-id"] = f"test_{i}"
                testing_block.append(initial_soup)

            feature.parse_inline_data(soup)

            html = str(soup)

            outputs = [i[1] for i in test_data]
            for i, output in enumerate(outputs):
                self.assertInHTML(
                    output,
                    html
                )
