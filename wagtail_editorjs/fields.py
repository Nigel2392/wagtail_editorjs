from django.db import models

from .forms import EditorJSFormField


class EditorJSField(models.JSONField):
    def __init__(self,
            features = None,
            *args, **kwargs
        ):
        self.features = features
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['features'] = self.features
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': EditorJSFormField,
            'features': self.features,
            **kwargs
        })
