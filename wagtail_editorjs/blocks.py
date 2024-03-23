from django.utils.functional import cached_property
from wagtail import blocks

from .render import render_editorjs_html
from .forms import (
    EditorJSFormField,
    get_features,
)


class EditorJSBlock(blocks.FieldBlock):
    def __init__(self, features=None, **kwargs):
        self._features = features
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        return EditorJSFormField(
            features=self.features,
            label=getattr(self.meta, 'label', None),
            required=getattr(self.meta, 'required', True),
            help_text=getattr(self.meta, 'help_text', ''),
        )

    @property
    def features(self):
        return get_features(self._features)

    def render(self, value, context=None):
        return render_editorjs_html(self.features, value, context)



