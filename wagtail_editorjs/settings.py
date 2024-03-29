from django.conf import settings as django_settings


"""
Clean the HTML output of the EditorJS field using bleach.
This will remove any tags or attributes not allowed by the EditorJS features.
If you want to disable this, set it to False.

Optionally; cleaning can be FORCED by passing `clean=True` to the `render_editorjs_html` function.
"""
CLEAN_HTML = getattr(django_settings, 'EDITORJS_CLEAN_HTML', True)

"""
Add a block ID to each editorJS block when rendering.
This is useful for targeting the block with JavaScript,
or possibly creating some link from frontend to admin area.
"""
ADD_BLOCK_ID = getattr(django_settings, 'EDITORJS_ADD_BLOCK_ID', True)

"""
The attribute name to use for the block ID.
This is only used if `ADD_BLOCK_ID` is True.
"""
BLOCK_ID_ATTR = getattr(django_settings, 'EDITORJS_BLOCK_ID_ATTR', 'data-editorjs-block-id')

