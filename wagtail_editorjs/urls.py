from django.urls import path, include
from .views import images

app_name = 'wagtail_editorjs'


urlpatterns = [
    # URL to format in javascript side.
    path('images/', images.image_for_id, name='image_for_id_fmt'),
    path('images/<int:image_id>/', images.image_for_id, name='image_for_id'),
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
