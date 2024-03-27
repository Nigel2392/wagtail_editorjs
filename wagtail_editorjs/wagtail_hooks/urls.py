from django.urls import path, include
from wagtail import hooks


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = []

    # Make sure all features are properly registered.
    from ..registry import EDITOR_JS_FEATURES
    EDITOR_JS_FEATURES._look_for_features()

    for hook in hooks.get_hooks("register_editorjs_urls"):
        urls += hook()

    return [
        path(
            'wagtail-editorjs/',
            name='wagtail_editorjs',
            view=include(
                (urls, 'wagtail_editorjs'),
                namespace='wagtail_editorjs'
            ),
        ),
    ]

