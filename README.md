wagtail_editorjs
================

A Wagtail EditorJS widget with page/image chooser support, document support and more!

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


   class HomePage(Page):
       content_panels = [
           FieldPanel("editor_field"),
       ]
       editor_field = EditorJSField(
           # All supported features
           features=[
               'attaches',
               'checklist',
               'code',
               'delimiter',
               'header',
               'image',
               'inline-code',
               'marker',
               'nested-list',
               'paragraph',
               'quote',
               'raw',
               'table',
               'underline',
               'warning',
               'link',
               'text-alignment-tune',
               'text-variant-tune'
           ],
           blank=True,
           null=True,
       )

   ```
