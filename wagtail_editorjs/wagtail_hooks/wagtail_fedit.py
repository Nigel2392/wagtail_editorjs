from wagtail_editorjs.render import render_editorjs_html
from wagtail_editorjs.registry import EditorJSValue
from wagtail_editorjs.fields import EditorJSField
from wagtail import hooks



@hooks.register("wagtail_fedit.register_type_renderer")
def register_renderers(renderer_map):

    # This is a custom renderer for RichText fields.
    # It will render the RichText field as a RichText block.
    renderer_map[EditorJSValue] = lambda request, context, instance, value: render_editorjs_html(
        value.features,
        value,
        context=context,
    )

@hooks.register("wagtail_fedit.field_editor_size")
def field_editor_size(model_instance, model_field):
    if isinstance(model_field, EditorJSField):
        return "full"
    return None
