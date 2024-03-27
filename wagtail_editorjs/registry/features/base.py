from typing import Any, Union
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from ..value import (
    EditorJSBlock,
)


class TemplateNotSpecifiedError(Exception):
    pass


class BaseEditorJSFeature:
    allowed_tags: list[str] = None
    allowed_attributes: dict[str, list[str]] = None
    # cleaner_funcs: dict[str, dict[str, Callable[[str], bool]]] = {}
    
    def __init__(self,
            tool_name: str,
            klass: str,
            js: Union[str, list[str]] = None,
            css: Union[str, list[str]] = None,
            include_template: str = None,
            config: dict = None,
            weight: int = 0, # Weight is used to manage which features.js files are loaded first.
            allowed_tags: list[str] = None,
            allowed_attributes: dict[str, list[str]] = None,
            **kwargs
        ):
        
        self.tool_name = tool_name
        self.klass = klass
        self.js = js or []
        self.css = css or []
        self.config = config or dict()
        self.kwargs = kwargs
        self.weight = weight
        self.include_template = include_template

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

    def __repr__(self):
        return f"<EditorJSFeature \"{self.tool_name}\">"
    
    @classmethod
    def get_test_data(cls):
        return []

    def get_template_context(self, context: dict[str, Any] = None) -> dict:
        return context
    
    def render_template(self, context: dict[str, Any] = None):
        if self.include_template and hasattr(self.include_template, "render"):
            return self.include_template.render(self.get_template_context(context))
        elif self.include_template:
            context = self.get_template_context(context)
            rendered = render_to_string(self.include_template, context)
            return mark_safe(rendered)
        raise TemplateNotSpecifiedError("Template not specified for this feature")
    
    def get_config(self, context: dict[str, Any] = None) -> dict:
        config = {
            "class": self.klass,
        }
        
        if self.config:
            config["config"] = self.config

        if self.kwargs:
            config.update(self.kwargs)

        return config

    def get_js(self):
        if isinstance(self.js, str):
            return [self.js]
        return self.js
    
    def get_css(self):
        if isinstance(self.css, str):
            return [self.css]
        return self.css
    
    def validate(self, data: Any):
        pass

    def create_block(self, tools: list[str], data: dict) -> EditorJSBlock:
        return EditorJSBlock(data, tools)
