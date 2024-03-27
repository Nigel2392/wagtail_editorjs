from django.utils.functional import cached_property
from wagtail import blocks

from .render import render_editorjs_html
from .forms import (
    EditorJSFormField,
    get_features,
)


class EditorJSBlock(blocks.FieldBlock):
    """
        A Wagtail block which can be used to add the EditorJS
        widget into any streamfield or structblock.
    """
    def __init__(self, features: list[str] = None, tools_config: dict = None, **kwargs):
        self._features = features
        self.tools_config = tools_config or {}
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        return EditorJSFormField(
            features=self.features,
            tools_config=self.tools_config,
            label=getattr(self.meta, 'label', None),
            required=getattr(self.meta, 'required', True),
            help_text=getattr(self.meta, 'help_text', ''),
        )
    
    @property
    def features(self):
        return get_features(self._features)

    def render(self, value, context=None):
        """
            Render the block value into HTML.
            This is so the block can be automatically included with `{% include_block my_editor_js_block %}`.
        """
        return render_editorjs_html(self.features, value, context)



