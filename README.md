wagtail_editorjs
================

*Check out [Awesome Wagtail](https://github.com/springload/awesome-wagtail) for more awesome packages and resources from the Wagtail community.*

A Wagtail EditorJS widget with page/image chooser support, document support and more!

## Add features:

* [Add an EditorJS feature](https://github.com/Nigel2392/wagtail_editorjs/blob/main/docs/editorjs_feature.md "Simple Image Feature")
* [Add an EditorJS tune](https://github.com/Nigel2392/wagtail_editorjs/blob/main/docs/tunes.md "text-alignment-tune") (Already exists in `wagtail_editorjs`, just an example.)

Quick start
-----------

1. Add 'wagtail_editorjs' to your INSTALLED_APPS setting like this:

   ```
   INSTALLED_APPS = [
   ...,
   'wagtail_editorjs',
   ]
   ```
2. Add the HTML to your template:

   ```django-html
   <link rel="stylesheet" href="{% static 'wagtail_editorjs/css/frontend.css' %}">
   {% load editorjs %}

   {# CSS files for features #}
   {% editorjs_static "css" %}

   {% editorjs self.editor_field %}

    {# JS files for features #}
    {% editorjs_static "js" %}
   ```
3. Add the field to your model:

   ```python
   ...
   from wagtail_editorjs.fields import EditorJSField
   from wagtail_editorjs.blocks import EditorJSBlock


   class HomePage(Page):
       content_panels = [
           FieldPanel("editor_field"),
           FieldPanel("content"),
       ]
       editor_field = EditorJSField(
           # All supported features
           features=[
               'attaches',
               'background-color-tune',
               'button',
               'checklist',
               'code',
               'delimiter',
               'document',
               'drag-drop',
               'header',
               'image',
               'images',
               'inline-code',
               'link',
               'link-autocomplete',
               'marker',
               'nested-list',
               'paragraph',
               'quote',
               'raw',
               'table',
               'text-alignment-tune',
               'text-color-tune',
               'text-variant-tune',
               'tooltip',
               'underline',
               'undo-redo',
               'warning'
            ],
           blank=True,
           null=True,
       )

       # Or as a block
       content = fields.StreamField([
           ('editorjs', EditorJSBlock(features=[
               # ... same as before
           ])),
       ], blank=True, use_json_field=True)
   ```

## List features

This readme might not fully reflect which features are available.

To find this out - you can:

1. start the python shell

   ```bash
   py ./manage.py shell
   ```
2. Print all the available features:

   ```python
   from wagtail_editorjs.registry import EDITOR_JS_FEATURES
   print(EDITOR_JS_FEATURES.keys())
   dict_keys([... all registered features ...])
   ```

##  Register a Wagtail block as a feature

It is also possible to register a Wagtail block as a feature.

This may be a `Fieldblock` (like `Charblock`, or `TextBlock`), or a `StructBlock`.

It is **not** allowed to be:

* A `StreamBlock`
* A `ListBlock`
* Any type of `ChooserBlock`
* A `RichTextBlock`

Example:

```python
from wagtail import hooks
from wagtail_editorjs.features import (
    WagtailBlockFeature,
    EditorJSFeatureStructBlock,
)
from wagtail_editorjs.registry import (
    EditorJSFeatures,
)
from wagtail_editorjs.hooks import REGISTER_HOOK_NAME

from wagtail import blocks

class HeadingBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    subtitle = blocks.CharBlock()

class RowBlock(EditorJSFeatureStructBlock):
    heading = HeadingBlock()
    body = blocks.TextBlock()

    class Meta:
        allowed_tags = ["div", "h1", "h2", "h3", "h4", "h5", "h6", "p"]

    def render(self, value, context=None):
        return f"<div><h1>{value['heading']['title']}</h1><h2>{value['heading']['subtitle']}</h2><p>{value['body']}</p></div>"

@hooks.register(REGISTER_HOOK_NAME)
def register_editor_js_features(registry: EditorJSFeatures):

    registry.register(
        "wagtail-row-block",
        WagtailBlockFeature(
            "wagtail-row-block",
            block=RowBlock(),
        ),
    )
```

## Settings

### `EDITORJS_CLEAN_HTML`

Default: `True`
Clean the HTML output on rendering.
This happens every time the field is rendered.
It might be smart to set up some sort of caching mechanism.
Optionally; cleaning can be FORCED by passing `clean=True` or `False` to the  `render_editorjs_html` function.

### `EDITORJS_ADD_BLOCK_ID`

Default: `true`
Add a block ID to each editorJS block when rendering.
This is useful for targeting the block with JavaScript,
or possibly creating some link from frontend to admin area.

### `EDITORJS_BLOCK_ID_ATTR`

Default: `data-editorjs-block-id`
The attribute name to use for the block ID.
This is only used if  `ADD_BLOCK_ID` is True.

### `EDITORJS_USE_FULL_URLS`

Default: `False`
Use full urls if the request is available in the EditorJS rendering context.