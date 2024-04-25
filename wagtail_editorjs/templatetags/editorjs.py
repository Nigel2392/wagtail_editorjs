from django import (
    template,
    forms,
)
from ..render import render_editorjs_html
from ..registry import EDITOR_JS_FEATURES, EditorJSValue
from ..forms import _get_feature_scripts

register = template.Library()

@register.simple_tag(takes_context=True, name="editorjs")
def render_editorjs(context, data: EditorJSValue):
    return render_editorjs_html(data.features, data, context=context)


init_scripts = {
    "css": [
        'wagtail_editorjs/css/frontend.css',
    ]
}


@register.simple_tag(takes_context=False, name="editorjs_static")
def editorjs_static(type_of_script="css", features: list[str] = None):
    if type_of_script not in ["css", "js"]:
        raise ValueError("type_of_script must be either 'css' or 'js'")

    if features is None:
        features = EDITOR_JS_FEATURES.keys()

    feature_mapping = EDITOR_JS_FEATURES.get_by_weight(
        features
    )

    frontend_static = init_scripts.get(type_of_script, [])
    for feature in feature_mapping.values():

        frontend_static.extend(
            _get_feature_scripts(
                feature,
                f"get_frontend_{type_of_script}",
                list_obj=frontend_static,
            )
        )

    kwargs = {}
    if type_of_script == "css":
        kwargs["css"] = {
            "all": frontend_static,
        }
    elif type_of_script == "js":
        kwargs["js"] = frontend_static

    return forms.Media(**kwargs).render()


