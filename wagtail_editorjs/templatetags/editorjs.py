from django import template
from ..render import render_editorjs_html
from ..registry import EDITOR_JS_FEATURES, EditorJSValue

register = template.Library()

@register.simple_tag(takes_context=True, name="editorjs")
def render_editorjs(context, data: EditorJSValue):
    return render_editorjs_html(data.features, data, context=context)

