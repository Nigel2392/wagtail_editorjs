from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from .forms import EditorJSFormField, EditorJSWidget



class DjangoEditorJSFormField(EditorJSFormField):
    @cached_property
    def widget(self):
        return EditorJSDjangoWidget(
            features=self.features,
            tools_config=self.tools_config,
        )



class EditorJSDjangoWidget(EditorJSWidget):
    """
        Taken from wagtail.
        This class is deprecated in wagtail 7.0
        This might still be useful if we have wagtail installed
        but would like to use the editorjs widget in a non-wagtailadmin form.
    """
    def render_html(self, name, value, attrs):
        """Render the HTML (non-JS) portion of the field markup"""
        return super().render(name, value, attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # no point trying to come up with sensible semantics for when 'id' is missing from attrs,
        # so let's make sure it fails early in the process
        try:
            id_ = attrs["id"]
        except (KeyError, TypeError):
            raise TypeError(
                "WidgetWithScript cannot be rendered without an 'id' attribute"
            )

        value_data = self.get_value_data(value)
        widget_html = self.render_html(name, value_data, attrs)

        js = self.render_js_init(id_, name, value_data)
        out = f"{widget_html}<script type=\"text/javascript\">{js}</script>"
        return mark_safe(out)

    def render_js_init(self, id_, name, value):
        # Adapted from editorjs-widget-controller.js
        return """
let editorJSWidget__wrapper = document.querySelector(`#${id}-wagtail-editorjs-widget-wrapper`);
let editorJSWidget__configElem = editorJSWidget__wrapper.querySelector(`#wagtail-editorjs-config`);
let editorJSWidget__config = JSON.parse(editorJSWidget__configElem.textContent);
let editorJSWidget__keys = Object.keys(editorJSWidget__config.tools);
for (let i = 0; i < editorJSWidget__keys.length; i++) {
    const key = editorJSWidget__keys[i];
    const toolConfig = editorJSWidget__config.tools[key];
    const toolClass = window[toolConfig.class];
    toolConfig.class = toolClass;
    editorJSWidget__config.tools[key] = toolConfig;
}
let editorJSWidget__element = document.querySelector(`#${id}`);
new window.EditorJSWidget(
    editorJSWidget__wrapper,
    editorJSWidget__element,
    editorJSWidget__config,
);
""" % {
            "id": id_,
        }

