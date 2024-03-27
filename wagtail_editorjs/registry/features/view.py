from typing import TYPE_CHECKING
from django.urls import path
from django.http import HttpRequest, HttpResponseNotAllowed
from wagtail import hooks

if TYPE_CHECKING:
    from ..feature_registry import EditorJSFeatures


class FeatureViewMixin:

    def handler(self, request: HttpRequest, *args, **kwargs):
        method = request.method.lower()
        if not hasattr(self, f"handle_{method}"):
            return self.method_not_allowed(request)
        
        view_func = getattr(self, f"handle_{method}")
        return view_func(request, *args, **kwargs)

    def method_not_allowed(self, request: HttpRequest):
        methods = ["get", "post", "put", "patch", "delete"]
        methods = [m for m in methods if hasattr(self, f"handle_{m}")]
        return HttpResponseNotAllowed(methods)

    def get_urlpatterns(self):
        return [
            path(
                f"{self.tool_name}/",
                self.handler,
                name=self.tool_name,
            )
        ]

    def on_register(self, registry: "EditorJSFeatures"):
        super().on_register(registry)
        @hooks.register("register_editorjs_urls")
        def register_admin_urls():
            return self.get_urlpatterns()

