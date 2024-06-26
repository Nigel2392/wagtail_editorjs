from django.test import TestCase
from wagtail_editorjs.registry.element.element import EditorJSElement
from wagtail_editorjs.registry.element.utils import (
    wrap_tag,
    _make_attr,
    add_attributes,
    EditorJSElementAttribute,
    EditorJSStyleAttribute,
)


class TestEditorJSElement(TestCase):

    def test_element(self):
        element = EditorJSElement(
            "div",
            "Hello, World!",
            attrs = {
                "class": "test-class",
                "id": "test-id",
            }
        )

        self.assertHTMLEqual(
            str(element),
            '<div class="test-class" id="test-id">Hello, World!</div>'
        )

    def test_element_attrs(self):
        element = EditorJSElement(
            "div",
            "Hello, World!",
        )

        element = add_attributes(element, **{
            "class_": "test-class",
            "data-test": "test-data",
        })

        self.assertHTMLEqual(
            str(element),
            '<div class="test-class" data-test="test-data">Hello, World!</div>'
        )

    def test_make_attr(self):

        attrs = _make_attr({
            "color": "red",
            "background-color": "blue",
        })

        self.assertIsInstance(attrs, EditorJSStyleAttribute)
        self.assertEqual(
            str(attrs),
            'color: red;background-color: blue'
        )

        attrs = _make_attr("test-class")
        self.assertIsInstance(attrs, EditorJSElementAttribute)
        self.assertEqual(
            str(attrs),
            'test-class'
        )

    def test_wrap_tag(self):
        tag = wrap_tag(
            "div",
            {
                "class": "test-class",
                "id": "test-id",
            },
            "Hello, World!"
        )
    
        self.assertHTMLEqual(
            tag,
            '<div class="test-class" id="test-id">Hello, World!</div>'
        )
    
    def test_wrap_tag_styles(self):
        tag = wrap_tag(
            "div",
            {
                "id": "test-id",
                "class": ["test-class", "test-class-2"],
                "style": {
                    "color": "red",
                    "background-color": "blue",
                }
            },
            "Hello, World!"
        )

        self.assertHTMLEqual(
            tag,
            '<div id="test-id" class="test-class test-class-2" style="color: red;background-color: blue">Hello, World!</div>'
        )

    
