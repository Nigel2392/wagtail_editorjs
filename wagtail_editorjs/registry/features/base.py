from typing import Any, Union, Mapping, Literal, TYPE_CHECKING
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from ..value import (
    EditorJSBlock,
)

if TYPE_CHECKING:
    from ..feature_registry import EditorJSFeatures


class TemplateNotSpecifiedError(Exception):
    pass


I18nDictionary = Mapping[
    Literal["ui", "toolNames", "tools", "blockTunes"],
    Mapping[str, str]
]

class PageChooserURLsMixin:
    def get_config(self, context: dict[str, Any] = None) -> dict:
        config = super().get_config(context)
        config.setdefault("config", {})
        config["config"]["chooserUrls"] = {
            "pageChooser": reverse_lazy(
                "wagtailadmin_choose_page",
            ),
            "externalLinkChooser": reverse_lazy(
                "wagtailadmin_choose_page_external_link",
            ),
            "emailLinkChooser": reverse_lazy(
                "wagtailadmin_choose_page_email_link",
            ),
            "phoneLinkChooser": reverse_lazy(
                "wagtailadmin_choose_page_phone_link",
            ),
            "anchorLinkChooser": reverse_lazy(
                "wagtailadmin_choose_page_anchor_link",
            ),
        },
        return config


class BaseEditorJSFeature:
    allowed_tags: list[str] = None
    allowed_attributes: dict[str, list[str]] = None
    klass: str = None
    js: list[str] = None
    css: list[str] = None
    frontend_css: list[str] = []
    frontend_js: list[str] = []
    # cleaner_funcs: dict[str, dict[str, Callable[[str], bool]]] = {}
    
    def __init__(self,
            tool_name: str,
            klass: str = None,
            js: Union[str, list[str]] = None,
            css: Union[str, list[str]] = None,
            include_template: str = None,
            config: dict = None,
            weight: int = 0, # Weight is used to manage which features.js files are loaded first.
            allowed_tags: list[str] = None,
            allowed_attributes: dict[str, list[str]] = None,
            **kwargs
        ):

        if not klass and not self.klass:
            raise ValueError("klass must be provided")
        
        if not klass:
            klass = self.klass
        
        self.tool_name = tool_name
        self.klass = klass
        self.config = config or dict()
        self.kwargs = kwargs
        self.weight = weight
        self.include_template = include_template

        self.init_static(
            css, js,
        )

        self.init_attrs(
            allowed_tags, allowed_attributes,
        )

    def value_for_form(self, value: dict) -> dict:
        """
            Prepare the value for the feature.
            This is useful for when you need to modify the data
            before it is passed to the frontend.
        """
        return value

    def init_static(self, css, js):
        css = css or []
        js = js or []

        if self.css:
            css.extend(self.css)

        if self.js:
            js.extend(self.js)
            
        self.js = js
        self.css = css

    def init_attrs(self, allowed_tags, allowed_attributes):
        if not isinstance(allowed_tags, (list, tuple, set)) and allowed_tags is not None:
            raise ValueError("allowed_tags must be a list, tuple or set")
        
        if not isinstance(allowed_attributes, dict) and allowed_attributes is not None:
            raise ValueError("allowed_attributes must be a dict")

        allowed_tags = allowed_tags or []
        allowed_attributes = allowed_attributes or dict()
       
        if self.allowed_tags:
            allowed_tags.extend(self.allowed_tags)

        if self.allowed_attributes:

            if isinstance(self.allowed_attributes, dict):
                for key, value in self.allowed_attributes.items():
                    allowed_attributes[key] = set(allowed_attributes.get(key, []) + value)
            elif isinstance(self.allowed_attributes, list):
                if not self.allowed_tags:
                    raise ValueError("Allowed attributes is specified as a list without allowed tags; provide allowed tags.")
                
                for tag in self.allowed_tags:
                    allowed_attributes[tag] = set(allowed_attributes.get(tag, []) + self.allowed_attributes)
            else:
                raise ValueError("Invalid allowed attributes type, self.allowed_attributes must be dict or list")

        self.allowed_tags = set(allowed_tags)
        self.allowed_attributes = allowed_attributes

    def on_register(self, registry: "EditorJSFeatures"):
        """
            Called when the feature is registered.
            This can be used to say; register URLs
            required for this feature to work.
        """
        pass

    def __repr__(self):
        return f"<EditorJSFeature \"{self.tool_name}\">"
    
    @classmethod
    def get_test_data(cls):
        """
            Returns test data for the feature.
            This is so it can easily be integrated with our tests.
            Any extra testing you deem necessary should be done in
            separate tests.
        """
        return []

    def get_template_context(self, context: dict[str, Any] = None) -> dict:
        """
            Returns the context for the template. (if any template is provided)
        """
        return context
    
    def render_template(self, context: dict[str, Any] = None):
        """
            Renders a template inside of the widget container.
            This is useful for things like the image feature.
        """
        if self.include_template and hasattr(self.include_template, "render"):
            return self.include_template.render(self.get_template_context(context))
        elif self.include_template:
            context = self.get_template_context(context)
            rendered = render_to_string(self.include_template, context)
            return mark_safe(rendered)
        raise TemplateNotSpecifiedError("Template not specified for this feature")
    
    def get_config(self, context: dict[str, Any] = None) -> dict:
        """
            Returns the config for the feature.
            This is what will be passed to javascript.
            The `class` is extracted from window[`class`].
        """
        config = {
            "class": self.klass,
        }
        
        if self.config:
            config["config"] = self.config

        if self.kwargs:
            config.update(self.kwargs)

        return config
    
    def get_translations(self) -> I18nDictionary:
        return {}

    def get_js(self):
        """
            Return any javascript files required for this feature to work.
        """
        if not self.js:
            return []
            
        if isinstance(self.js, str):
            return [self.js]
        return self.js
    
    def get_css(self):
        """
            Return any css files required for this feature to work.
        """
        if not self.css:
            return []
            
        if isinstance(self.css, str):
            return [self.css]
        return self.css
    
    def get_frontend_css(self):
        """
            Returns the css files required for the frontend.
        """
        return self.frontend_css
    
    def get_frontend_js(self):
        """
            Returns the js files required for the frontend.
        """
        return self.frontend_js

    def validate(self, data: Any):
        """
            Validate any data coming from editorJS
            for completeness and correctness.
        """
        pass

    def create_block(self, tools: list[str], data: dict) -> EditorJSBlock:
        """
            Create a block from the data.
            This block is the value that the developer will work with.
            It is a subclass of `dict`.
        """
        return EditorJSBlock(data, tools)
