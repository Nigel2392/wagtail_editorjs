from typing import Any
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.admin.widgets import AdminPageChooser
from wagtail.documents.widgets import AdminDocumentChooser
from wagtail.documents import get_document_model
from wagtail import hooks

from ..registry import (
    ModelInlineEditorJSFeature,
    FeatureViewMixin,
)
from django.http import (
    HttpResponse,
    JsonResponse,
)


Document = get_document_model()


class BasePageLinkMixin:
    @classmethod
    def get_url(cls, instance):
        return instance.get_url()

    @classmethod
    def get_full_url(cls, instance, request):
        return instance.get_full_url(request)
    
    @classmethod
    def get_test_queryset(cls):
        return super().get_test_queryset().filter(depth__gt=1)

class LinkFeature(BasePageLinkMixin, ModelInlineEditorJSFeature):
    allowed_tags = ["a"]
    allowed_attributes = ["class", "href", "data-id"]
    must_have_attrs = {
        "data-parent-id": None,
    }
    chooser_class = AdminPageChooser
    model = Page
    
    @classmethod
    def get_test_data(cls):
        models = cls.get_test_queryset()[0:5]
        return [
            (
                # Override to add data-autocomplete.
                f"<a data-id='{model.id}' data-{cls.model._meta.model_name}='True' data-parent-id='this-doesnt-get-used'></a>",
                f"<a href='{cls.get_url(model)}' class='{cls.model._meta.model_name}-link'></a>",
            )
            for model in models
        ]


SEARCH_QUERY_PARAM = "search"
CONSTRUCT_PAGE_QUERYSET = "construct_page_queryset"
BUILD_PAGE_DATA = "build_page_data"


class LinkAutoCompleteFeature(FeatureViewMixin, BasePageLinkMixin, ModelInlineEditorJSFeature):
    allowed_tags = ["a"]
    allowed_attributes = ["class", "href", "data-id"]
    must_have_attrs = {
        "data-autocomplete": "page",
    }
    chooser_class = AdminPageChooser
    model = Page

    def get_config(self, context: dict[str, Any]):
        config = super(ModelInlineEditorJSFeature, self).get_config(context)
        config.setdefault("config", {})
        config["config"]["endpoint"] = reverse(f"wagtail_editorjs:{self.tool_name}")
        config["config"]["queryParam"] = "search"
        return config

    @classmethod
    def get_test_data(cls):
        models = cls.get_test_queryset()[0:5]
        return [
            (
                # Override to add data-autocomplete.
                f"<a data-id='{model.id}' data-{cls.model._meta.model_name}='True' data-autocomplete='page'></a>",
                f"<a href='{cls.get_url(model)}' class='{cls.model._meta.model_name}-link'></a>",
            )
            for model in models
        ]

    def handle_get(self, request):
        """
        Autocomplete for internal links
        """
        search = request.GET.get(SEARCH_QUERY_PARAM)

        pages = Page.objects.all()\
            .live()\
            .specific()

        for fn in hooks.get_hooks(CONSTRUCT_PAGE_QUERYSET):
            pages = fn(request, pages, search)

            if isinstance(pages, HttpResponse):
                return pages

        if search:
            pages = pages.search(search)


        page_list = []
        page_data_hooks = hooks.get_hooks(BUILD_PAGE_DATA)
        for page in pages:
            data = {
                'id': page.id,
                'name': page.title,
                'href': page.get_url(request),
                'description': page.search_description,
                'autocomplete': 'page',
                'page': True,
            }

            for hook in page_data_hooks:
                hook(request, page, data)

            page_list.append(data)


        return JsonResponse({
                "success": True,
                "items": page_list,
            },
            status=200,
        )


class DocumentFeature(ModelInlineEditorJSFeature):
    allowed_tags = ["a"]
    allowed_attributes = ["class", "href", "data-id"]
    chooser_class = AdminDocumentChooser
    model = Document

    @classmethod
    def get_url(cls, instance):
        return instance.file.url

