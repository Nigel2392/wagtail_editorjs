from typing import Any
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.admin.widgets import AdminPageChooser
from wagtail.documents.widgets import AdminDocumentChooser
from wagtail.documents import get_document_model
from wagtail import hooks

from ..registry import (
    PageChooserURLsMixin,
    InlineEditorJSFeature,
    ModelInlineEditorJSFeature,
    FeatureViewMixin,
)
from django.http import (
    HttpResponse,
    JsonResponse,
)


Document = get_document_model()


class TooltipFeature(InlineEditorJSFeature):
    allowed_tags = ["span"]
    allowed_attributes = [
        "class",
        "data-tippy-content",
        "data-tippy-placement",
        "data-tippy-follow-cursor",
    ]
    tag_name = "span"
    must_have_attrs = {
        "class": "wagtail-tooltip",
        "data-w-tooltip-content-value": None,
    }
    can_have_attrs = {
        "data-w-tooltip-placement-value": None,
    }
    
    klass = "WagtailTooltip"
    js = [
        "wagtail_editorjs/js/tools/tooltips/wagtail-tooltips.js",
    ]
    frontend_js = [
        "wagtail_editorjs/vendor/tippy/popper.min.js",
        "wagtail_editorjs/vendor/tippy/tippy-bundle.min.js",
        "wagtail_editorjs/js/tools/tooltips/frontend.js",
    ]

    @classmethod
    def get_test_data(cls):
        return [
            (
                f"<span class='wagtail-tooltip' data-w-tooltip-content-value='Tooltip content'></span>",
                f"<span class='wagtail-tooltip' data-tippy-content='Tooltip content' data-tippy-placement='bottom' data-tippy-follow-cursor='horizontal'></span>",
            ),
            (
                f"<span class='wagtail-tooltip' data-w-tooltip-content-value='Tooltip content' data-w-tooltip-placement-value='top'></span>",
                f"<span class='wagtail-tooltip' data-tippy-content='Tooltip content' data-tippy-placement='top' data-tippy-follow-cursor='horizontal'></span>",
            ),
        ]

    def build_elements(self, inline_data: list, context: dict[str, Any] = None) -> list:
        for element, attrs in inline_data:

            element.attrs.clear()
            element["class"] = "wagtail-tooltip"

            element["data-tippy-follow-cursor"] = "horizontal"

            # As per wagtail documentation default is bottom.
            attrs.setdefault("data-w-tooltip-placement-value", "bottom")

            for k, v in attrs.items():
                if not k.startswith("data-w-tooltip-") or not k.endswith("-value"):
                    continue

                k = k.replace("data-w-tooltip-", "data-tippy-")
                k = k[:-6]

                element[k] = v


class BasePageLinkMixin(PageChooserURLsMixin):
    allowed_attributes = ["target", "rel"]
    can_have_attrs = {
        "data-target": None,
        "data-rel": None,
    }

    def build_element(self, item, obj, context: dict[str, Any] = None, data: dict[str, Any] = None):
        """Build the element from the object."""
        super().build_element(item, obj, context, data)
        if "data-target" in data and data["data-target"]:
            item["target"] = data["data-target"]
        if "data-rel" in data and data["data-rel"]:
            item["rel"] = data["data-rel"]

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
    allowed_attributes = BasePageLinkMixin.allowed_attributes + [
        "class", "href", "data-id"
    ]
    must_have_attrs = {
        "data-parent-id": None,
    }
    chooser_class = AdminPageChooser
    model = Page

    klass="WagtailLinkTool"
    js = [
        "wagtail_editorjs/js/tools/wagtail-chooser-tool.js",
        "wagtail_editorjs/js/tools/wagtail-link.js",
    ]

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
    allowed_attributes = BasePageLinkMixin.allowed_attributes + [
        "class", "href", "data-id"
    ]
    must_have_attrs = {
        "data-autocomplete": "page",
    }
    chooser_class = AdminPageChooser
    model = Page
    klass="LinkAutocomplete"
    js = [
        "wagtail_editorjs/vendor/editorjs/tools/link-autocomplete.js",
    ]

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
    klass = "WagtailDocumentTool"
    js = [
        "wagtail_editorjs/js/tools/wagtail-chooser-tool.js",
        "wagtail_editorjs/js/tools/wagtail-document.js",
    ]

    @classmethod
    def get_url(cls, instance):
        return instance.file.url

