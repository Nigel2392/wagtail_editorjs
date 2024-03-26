from django.conf import settings as django_settings



CLEAN_HTML = getattr(django_settings, 'EDITORJS_CLEAN_HTML', True)