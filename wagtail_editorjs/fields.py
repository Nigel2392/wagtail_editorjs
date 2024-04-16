from typing import Any
from django.db import models
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from .forms import EditorJSFormField
from .registry import EDITOR_JS_FEATURES, get_features


class EditorJSField(models.JSONField):
    def __init__(self,
            features: list[str] = None,
            tools_config: dict  = None,
            *args, **kwargs
        ):
        self._features = features
        self.tools_config = tools_config or {}
        super().__init__(*args, **kwargs)

    @cached_property
    def features(self):
        return get_features(self._features)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['features'] = self.features
        kwargs['tools_config'] = self.tools_config
        return name, path, args, kwargs
    
    def from_db_value(self, value: Any, expression, connection) -> Any:
        value = super().from_db_value(
            value, expression, connection
        )
        return EDITOR_JS_FEATURES.to_python(
            self.features, value
        )
    
    def get_prep_value(self, value: Any) -> Any:
        value = EDITOR_JS_FEATURES.prepare_value(
            self.features, value
        )
        return super().get_prep_value(value)
    
    def to_python(self, value: Any) -> Any:
        value = super().to_python(value)
        return EDITOR_JS_FEATURES.to_python(
            self.features, value
        )
    
    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': EditorJSFormField,
            'features': self.features,
            'tools_config': self.tools_config,
            **kwargs
        })
