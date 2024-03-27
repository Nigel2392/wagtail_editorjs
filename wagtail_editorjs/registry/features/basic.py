from typing import Any, Union

from ..element import EditorJSElement
from ..value import EditorJSBlock
from .base import BaseEditorJSFeature


class EditorJSJavascriptFeature(BaseEditorJSFeature):
    def __init__(self, tool_name: str, js: Union[str, list[str]] = None, css: Union[str, list[str]] = None, weight: int = 0, allowed_tags: list[str] = None, allowed_attributes: dict[str, list[str]] = None):
        # 1 for klass - unused for this type of feature.
        super().__init__(tool_name, 1, js, css, None, {}, weight=weight, allowed_tags=allowed_tags, allowed_attributes=allowed_attributes)

    def get_config(self, context: dict[str, Any] = None) -> dict:
        return None


class EditorJSFeature(BaseEditorJSFeature):
    def validate(self, data: Any):
        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> "EditorJSElement":
        return EditorJSElement(
            "p",
            block["data"].get("text")
        )
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "text": "Hello, world!"
            }
        ]
    

class EditorJSTune(BaseEditorJSFeature):
    """
        Works mostly like EditorJSFeature, but is used for tunes.
        Handles validation differently.
    """

    def tune_element(self, element: "EditorJSElement", tune_value: Any, context = None) -> "EditorJSElement":
        return element
    
    @classmethod
    def get_test_data(cls):
        return None
