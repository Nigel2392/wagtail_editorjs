from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from ..render import render_editorjs_html
from ..registry import EDITOR_JS_FEATURES

register = template.Library()

@register.simple_tag(takes_context=True, name="editorjs")
def render_editorjs(context, data: dict):
    html = render_editorjs_html(list(EDITOR_JS_FEATURES.keys()), data, context=context)
    return render_to_string("wagtail_editorjs/rich_text.html", {"html": mark_safe(html)})
