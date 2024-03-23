from django.utils.functional import cached_property
from django import forms
from django.forms import (
    fields as formfields,
    widgets
)
from wagtail import hooks

from .hooks import (
    BUILD_CONFIG_HOOK,
)
from .registry import (
    EDITOR_JS_FEATURES,
    get_features,
    TemplateNotSpecifiedError,
)



class EditorJSWidget(widgets.Input):
    template_name = 'wagtail_editorjs/widgets/editorjs.html'
    input_type = 'hidden'

    def __init__(self, features: list[str] = None, attrs: dict = None):
        super().__init__(attrs)

        self.features = get_features(features)
        self.autofocus = self.attrs.get('autofocus', False)
        self.placeholder = self.attrs.get('placeholder', "")

    def build_attrs(self, base_attrs, extra_attrs):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-controller'] = 'editorjs-widget'
        return attrs
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        config = EDITOR_JS_FEATURES.build_config(self.features, context)
        config["holder"] = f"{context['widget']['attrs']['id']}-wagtail-editorjs-widget"

        for hook in hooks.get_hooks(BUILD_CONFIG_HOOK):
            hook(self, context, config)

        context['widget']['features'] = self.features
        inclusion_templates = []
        for feature in self.features:
            try:
                inclusion_templates.append(
                    EDITOR_JS_FEATURES[feature].render_template(context)
                )
            except TemplateNotSpecifiedError:
                pass
        
        context['widget']['inclusion_templates'] = inclusion_templates
        context['widget']['config'] = config
        return context
    
    @cached_property
    def media(self):
        js = [
            "wagtail_editorjs/vendor/editorjs.umd.js",
        ]
        css = [
            "wagtail_editorjs/css/editorjs-widget.css",
        ]

        for feature in self.features:
            js.extend(
                EDITOR_JS_FEATURES[feature].get_js()
            )
            css.extend(
                EDITOR_JS_FEATURES[feature].get_css()
            )

        js.extend([
            "wagtail_editorjs/js/editorjs-widget-controller.js",
            "wagtail_editorjs/js/editorjs-widget.js",
        ])

        return widgets.Media(
            js=js,
            css={'all': css}
        )
    


class EditorJSFormField(formfields.JSONField):
    def __init__(self, features: list[str] = None, *args, **kwargs):
        self.features = get_features(features)
        super().__init__(*args, **kwargs)

    @cached_property
    def widget(self):
        return EditorJSWidget(
            features=self.features,
        )
    
    def to_python(self, value):
        value = super().to_python(value)
        value = EDITOR_JS_FEATURES.to_python(
            self.features, value
        )

        return value
    
    def prepare_value(self, value):
        if value is None:
            return super().prepare_value(value)
        
        if isinstance(value, formfields.InvalidJSONInput):
            return value
        
        value = EDITOR_JS_FEATURES.prepare_value(
            self.features, value
        )

        return super().prepare_value(value)
    
    def validate(self, value) -> None:
        super().validate(value)
        if value is None and self.required:
            raise forms.ValidationError("This field is required")

        if not isinstance(value, dict):
            raise forms.ValidationError("Invalid JSON object")
        
        EDITOR_JS_FEATURES.validate_for_tools(
            self.features, value
        )



