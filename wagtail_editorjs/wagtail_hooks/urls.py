from ..urls import wagtail_urlpatterns
from wagtail import hooks

@hooks.register("register_admin_urls")
def register_admin_urls():
    return wagtail_urlpatterns
