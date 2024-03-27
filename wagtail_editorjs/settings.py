from django.conf import settings as django_settings


CLEAN_HTML = getattr(django_settings, 'EDITORJS_CLEAN_HTML', True)
CLEAN_HTML.__doc__ = """Clean the HTML output of the EditorJS field using bleach.
This will remove any tags or attributes not allowed by the EditorJS features.
If you want to disable this, set it to False.

Optionally; cleaning can be FORCED by passing `clean=True` to the `render_editorjs_html` function."""
