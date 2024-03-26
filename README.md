wagtail_editorjs
================

*Check out [Awesome Wagtail](https://github.com/springload/awesome-wagtail) for more awesome packages and resources from the Wagtail community.*

A Wagtail EditorJS widget with page/image chooser support, document support and more!

## Add features:

* [Add an already defined EditorJS feature](https://github.com/Nigel2392/wagtail_editorjs/blob/main/docs/editorjs_feature.md "Simple Image Feature")

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
   {% editorjs self.editor_field %}
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
             'marker',
             'nested-list',
             'paragraph',
             'quote',
             'raw',
             'table',
             'text-alignment-tune',
             'text-variant-tune',
             'underline',
             'undo-redo',
             'warning',
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


## Settings

### `EDITORJS_CLEAN_HTML`

Default: `True`
Clean the HTML output on rendering.
This happens every time the field is rendered.
It might be smart to set up some sort of caching mechanism.
