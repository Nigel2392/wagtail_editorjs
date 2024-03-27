from typing import Any
from .inlines import (
    ModelInlineEditorJSFeature,
)
from wagtail.snippets.widgets import AdminSnippetChooser


class SnippetChooserModel:
    """ Utility class for type annotations """

    def build_element(self, soup_elem, context = None): ...


class BaseInlineSnippetChooserFeature(ModelInlineEditorJSFeature):
    model: SnippetChooserModel = None
    widget = AdminSnippetChooser

    def build_element(self, soup_elem, obj: SnippetChooserModel, context: dict[str, Any] = None):
        return obj.build_element(soup_elem, context)




