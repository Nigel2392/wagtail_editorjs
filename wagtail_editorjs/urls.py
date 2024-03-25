from django.urls import path, include
from .views import (
    images,
    attaches,
)

app_name = 'wagtail_editorjs'


urlpatterns = [
    # URL to format in javascript side.
    path('images/', images.image_for_id, name='image_for_id_fmt'), # URL to format in javascript side.
    path('images/<int:image_id>/', images.image_for_id, name='image_for_id'),
    path('attaches/', attaches.attaches_upload, name='attaches_upload'),
]


# URL configuration to be included in wagtail admin urls.
wagtail_urlpatterns = [
    path(
        'wagtail-editorjs/',
        name='wagtail_editorjs',
        view=include(
            (urlpatterns, 'wagtail_editorjs'),
            namespace='wagtail_editorjs'
        ),
    ),
]
