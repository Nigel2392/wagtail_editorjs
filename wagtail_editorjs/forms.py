from django.utils.functional import cached_property
from django import forms
from django.forms import (
    fields as formfields,
    widgets
)
from wagtail import hooks

from datetime import datetime

from .hooks import (
    BUILD_CONFIG_HOOK,
)
from .registry import (
    EDITOR_JS_FEATURES,
    get_features,
    TemplateNotSpecifiedError,
)



class EditorJSWidget(widgets.Input):
    """
        A widget which renders the EditorJS editor.

        All features are allowed to register CSS and JS files.

        They can also optionally include sub-templates
        inside of the widget container.
    """
    template_name = 'wagtail_editorjs/widgets/editorjs.html'
    accepts_features = True
    input_type = 'hidden'

    def __init__(self, features: list[str] = None, tools_config: dict = None, attrs: dict = None):
        super().__init__(attrs)

        self.features = get_features(features)
        self.tools_config = tools_config or {}
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

        tools = config.get('tools', {})
        for tool_name, tool_config in self.tools_config.items():
            if tool_name in tools:
                cfg = tools[tool_name]
                cpy = tool_config.copy()
                cpy.update(cfg)
                tools[tool_name] = cpy
            else:
                raise ValueError(f"Tool {tool_name} not found in tools; did you include the feature?")

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
            "wagtail_editorjs/vendor/editorjs/editorjs.umd.js",
            "wagtail_editorjs/js/editorjs-widget.js",
            "wagtail_editorjs/js/tools/wagtail-block-tool.js",
        ]
        css = [
            "wagtail_editorjs/css/editorjs-widget.css",
            # "wagtail_editorjs/css/frontend.css",
        ]

        feature_mapping = EDITOR_JS_FEATURES.get_by_weight(
            self.features,
        )

        for feature in feature_mapping.values():
            for js_file in feature.get_js():
                if js_file not in js:
                    if isinstance(js_file, (list, tuple)):
                        js.extend(js_file)
                    else:
                        js.append(js_file)

            for css_file in feature.get_css():
                if css_file not in css:
                    if isinstance(css_file, (list, tuple)):
                        css.extend(css_file)
                    else:
                        css.append(css_file)

        js.extend([
            "wagtail_editorjs/js/editorjs-widget-controller.js",
        ])

        return widgets.Media(
            js=js,
            css={'all': css}
        )
    


class EditorJSFormField(formfields.JSONField):
    def __init__(self, features: list[str] = None, tools_config: dict = None, *args, **kwargs):
        self.features = get_features(features)
        self.tools_config = tools_config or {}
        super().__init__(*args, **kwargs)

    @cached_property
    def widget(self):
        return EditorJSWidget(
            features=self.features,
            tools_config=self.tools_config,
        )
    
    def to_python(self, value):
        value = super().to_python(value)

        if value is None:
            return value
        
        value = EDITOR_JS_FEATURES.to_python(
            self.features, value
        )

        return value
    
    def prepare_value(self, value):
        if value is None:
            return super().prepare_value(value)
        
        if isinstance(value, formfields.InvalidJSONInput):
            return value
        
        if not isinstance(value, dict):
            return value
        
        value = EDITOR_JS_FEATURES.prepare_value(
            self.features, value
        )

        return super().prepare_value(value)
    
    def validate(self, value) -> None:
        super().validate(value)

        if value is None and self.required:
            raise forms.ValidationError("This field is required")

        if value:
            if not isinstance(value, dict):
                raise forms.ValidationError("Invalid EditorJS JSON object, expected a dictionary")

            if "time" not in value:
                raise forms.ValidationError("Invalid EditorJS JSON object, missing time")
            
            if "version" not in value:
                raise forms.ValidationError("Invalid EditorJS JSON object, missing version")
            
            time = value["time"]
            if not isinstance(time, int):
                raise forms.ValidationError("Invalid EditorJS JSON object, time is not an integer")
            
            try:
                time = datetime.fromtimestamp(time)
            except ValueError:
                raise forms.ValidationError("Invalid EditorJS JSON object, time is not a valid timestamp")
            
            if time is None:
                raise forms.ValidationError("Invalid EditorJS JSON object, time is invalid")

        if value and self.required:
            if "blocks" not in value:
                raise forms.ValidationError("Invalid JSON object")
            
            if not value["blocks"]:
                raise forms.ValidationError("This field is required")

        EDITOR_JS_FEATURES.validate_for_tools(
            self.features, value
        )



