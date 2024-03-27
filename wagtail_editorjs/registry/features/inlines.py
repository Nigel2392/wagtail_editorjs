from typing import Any, Union
from django.utils.functional import cached_property

from .base import BaseEditorJSFeature

import bs4


class InlineEditorJSFeature(BaseEditorJSFeature):
    must_have_attrs = None
    can_have_attrs = None

    def __init__(
        self,
        tool_name: str,
        tag_name: str,
        klass: str = None,
        must_have_attrs: dict = None,
        can_have_attrs: dict = None,
        js: Union[str, list[str]] = None,
        css: Union[str, list[str]] = None,
        include_template: str = None,
        config: dict = None,
        weight: int = 0,
        allowed_tags: list[str] = None,
        allowed_attributes: dict[str, list[str]] = None,
        **kwargs,
    ):
        super().__init__(
            tool_name,
            klass,
            js,
            css,
            include_template,
            config,
            weight=weight,
            allowed_tags=allowed_tags,
            allowed_attributes=allowed_attributes,
            **kwargs,
        )

        must_have_attrs = must_have_attrs or {}
        can_have_attrs = can_have_attrs or {}

        if self.must_have_attrs:
            must_have_attrs.update(self.must_have_attrs)

        if self.can_have_attrs:
            can_have_attrs.update(self.can_have_attrs)

        self.tag_name = tag_name
        self.must_have_attrs = must_have_attrs
        self.can_have_attrs = can_have_attrs

    def build_elements(self, inline_data: list, context: dict[str, Any] = None) -> list:
        """
        Builds the elements for the inline data.

        See the LinkFeature class for an example.
        """
        pass

    def filter(self, item):
        """
        Filter function for the bs4 find_all method.
        Extracts the tag name and attributes from the item and compares them to the must_have_attrs.
        If the item attributes matches the must_have_attrs the element is what we need.
        """
        if item.name != self.tag_name:
            return False

        for key, value in self.must_have_attrs.items():
            if not value:
                if not item.has_attr(key):
                    return False
            else:
                cmp = item.get(key)
                if isinstance(cmp, str):
                    cmp = cmp.strip()
                    if cmp != value:
                        return False
                elif isinstance(cmp, list):
                    if value not in cmp:
                        return False
                else:
                    return False

        return True

    def parse_inline_data(self, soup: bs4.BeautifulSoup, context=None):
        """
        Finds inline elements by the must_have_attrs and can_have_attrs.
        Designed to be database-efficient; allowing for gathering of all data before
        making a database request.

        I.E. For a link; this would gather all page ID's and fetch them in a single query.
        """

        matches: dict[Any, dict[str, Any]] = {}
        elements = soup.find_all(self.filter)
        if not elements:
            return None

        for item in elements:
            matches[item] = {}

            for key in self.must_have_attrs.keys():
                matches[item][key] = item.get(key)

            for key, value in self.can_have_attrs.items():
                if value:
                    matches[item][key] = item.get(key)
                else:
                    if item.has_attr(key):
                        matches[item][key] = True

        # Build all inlines.
        self.build_elements(list(matches.items()), context=context)

    @classmethod
    def get_test_data(cls) -> list[tuple[str, str]]:
        """
        Returns a list of test data.

        The test data should be a list of tuples.

        The first item in the tuple is the raw HTML tag.
        The second item is the expected output.

        The raw HTML tag(s) will be randomly appended into a soup.
        We will use assertQueries(1) to ensure any database queries are kept to a minimum.
        """
        return []


class ModelInlineEditorJSFeature(InlineEditorJSFeature):
    model = None
    chooser_class = None
    tag_name = "a"
    id_attr = "data-id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tag_name=self.tag_name, **kwargs)
        self.must_have_attrs = self.must_have_attrs | {
            self.id_attr: None,
            f"data-{self.model._meta.model_name}": None,
        }

    @cached_property
    def widget(self):
        if self.chooser_class is None:
            return None
        
        return self.chooser_class()

    def get_id(self, item, attrs: dict[str, Any], context: dict[str, Any] = None):
        return int(attrs[self.id_attr])

    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"][
            "chooserId"
        ] = f"editorjs-{self.model._meta.model_name}-chooser-{context['widget']['attrs']['id']}"
        return config

    def render_template(self, context: dict[str, Any] = None):
        if not self.widget:
            return super().render_template(context)
        
        return self.widget.render_html(
            f"editorjs-{self.model._meta.model_name}-chooser-{context['widget']['attrs']['id']}",
            None,
            {
                "id": f"editorjs-{self.model._meta.model_name}-chooser-{context['widget']['attrs']['id']}"
            },
        )

    def build_element(self, item, obj, context: dict[str, Any] = None):
        """
        Build the element from the object.

        item:    bs4.element.Tag
        obj:     Model
        context: RequestContext | None
        """
        # delete all attributes
        for key in list(item.attrs.keys()):
            del item[key]

        request = None
        if context:
            request = context.get("request")
            item["href"] = self.get_full_url(obj, request)
        else:
            item["href"] = self.get_url(obj)
        item["class"] = f"{self.model._meta.model_name}-link"

    @classmethod
    def get_url(cls, instance):
        return instance.url

    @classmethod
    def get_full_url(cls, instance, request):
        return request.build_absolute_uri(cls.get_url(instance))

    def build_elements(self, inline_data: list, context: dict[str, Any] = None) -> list:
        """
        Process the bulk data; fetch all pages in one go
        and build the elements.
        """
        super().build_elements(inline_data, context=context)
        ids = []
        # element_soups = []
        for data in inline_data:
            # soup: BeautifulSoup
            # element: EditorJSElement
            # matches: dict[bs4.elementType, dict[str, Any]]
            # data: dict[str, Any] # Block data.
            item, data = data

            # # Store element and soup for later replacement of content.
            # element_soups.append((soup, element))

            # Item is bs4 tag, attrs are must_have_attrs

            id = self.get_id(item, data, context)
            ids.append((item, id))

            # delete all attributes
            for key in list(item.attrs.keys()):
                del item[key]

        # Fetch all objects
        objects = self.model.objects.in_bulk([id for item, id in ids])
        for item, id in ids:
            self.build_element(item, objects[id], context)

    def get_css(self):
        return self.widget.media._css.get("all", []) + super().get_css()

    def get_js(self):
        return (self.widget.media._js or []) + super().get_js()

    @classmethod
    def get_test_queryset(cls):
        return cls.model.objects.all()

    @classmethod
    def get_test_data(cls):
        # This test only works for the default build_element method.
        # Any extra attributes will make this test fail otherwise.
        if cls.build_element is not ModelInlineEditorJSFeature.build_element:
            raise ValueError(
                "You must implement the get_test_data method for your ModelInlineEditorJSFeature"
                "if you override the build_element method."
            )

        # Limit test QS to 5.
        models = cls.get_test_queryset()[0:5]
        return [
            (
                f"<a data-id='{model.id}' data-{cls.model._meta.model_name}='True'></a>",
                f"<a href='{cls.get_url(model)}' class='{cls.model._meta.model_name}-link'></a>",
            )
            for model in models
        ]
