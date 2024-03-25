"""
    This module defines mappings from tools to the editorjs javascript side.
"""

from collections import defaultdict, OrderedDict
from typing import Any, Union, Callable
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from wagtail import hooks

import copy, datetime, bs4

from .editorjs.element import (
    EditorJSElement,
)
from .hooks import (
    REGISTER_HOOK_NAME,
)


class TemplateNotSpecifiedError(Exception):
    pass



class EditorJSValue(dict):
    def __init__(self, data: dict, features: dict[str, "EditorJSFeature"]):
        self._features = features
        super().__init__(data)

    @property
    def blocks(self) -> list["EditorJSBlock"]:
        return self["blocks"]
    
    @property
    def time(self):
        time = self.get("time")
        if time is None:
            return None
        return datetime.datetime.fromtimestamp(time)
    
    @property
    def version(self):
        return self.get("version")
    
    @property
    def features(self) -> list["EditorJSFeature"]:
        return self._features


class EditorJSBlock(dict):
    def __init__(self, data: dict, features: list[str]):
        self.features = features
        super().__init__(data)

    @property
    def id(self):
        return self.get("id")
    
    @property
    def type(self):
        return self.get("type")
    
    @property
    def data(self):
        return self.get("data", {})
    
    @property
    def tunes(self):
        return self.get("tunes", {})


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


class EditorJSJavascriptFeature(BaseEditorJSFeature):
    def __init__(self, tool_name: str, js: Union[str, list[str]] = None, css: Union[str, list[str]] = None, weight: int = 0, allowed_tags: list[str] = None, allowed_attributes: dict[str, list[str]] = None):
        super().__init__(tool_name, None, js, css, None, {}, weight=weight, allowed_tags=allowed_tags, allowed_attributes=allowed_attributes)

    def get_config(self, context: dict[str, Any] = None) -> dict:
        return None


class EditorJSFeature(BaseEditorJSFeature):
    def validate(self, data: Any):
        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
    
    def render_block_data(self, block: EditorJSBlock, context = None) -> "EditorJSElement":
        return EditorJSElement(
            "p",
            block["data"].get("text")
        )
    
    @classmethod
    def get_test_data(cls):
        return [
            {
                "text": "Hello, world!"
            }
        ]
    

class EditorJSTune(BaseEditorJSFeature):
    """
        Works mostly like EditorJSFeature, but is used for tunes.
        Handles validation differently.
    """

    def tune_element(self, element: "EditorJSElement", tune_value: Any, context = None) -> "EditorJSElement":
        return element
    
    @classmethod
    def get_test_data(cls):
        return None


class BaseInlineEditorJSFeature(BaseEditorJSFeature):
    pass


class LazyInlineEditorJSFeature(BaseInlineEditorJSFeature):
    def __init__(self,
            tool_name: str,
            klass: str,
            tag_name: str,
            must_have_attrs: dict = None,
            can_have_attrs: dict = None,
            js: Union[str, list[str]] = None,
            css: Union[str, list[str]] = None,
            include_template: str = None,
            config: dict = None,
            weight: int = 0,
            allowed_tags: list[str] = None,
            allowed_attributes: dict[str, list[str]] = None,
            **kwargs
        ):
        super().__init__(tool_name, klass, js, css, include_template, config, weight=weight, allowed_tags=allowed_tags, allowed_attributes=allowed_attributes, **kwargs)
        self.tag_name = tag_name
        self.must_have_attrs = must_have_attrs or {}
        self.can_have_attrs = can_have_attrs or {}


    def build_elements(self, inline_data: list, context: dict[str, Any] = None) -> list:
        """
            Builds the elements for the inline data.

            See the LinkFeature class for an example.
        """
        pass
    

    def parse_inline_data(self, element: EditorJSElement, data: Any, context = None) -> tuple[bs4.BeautifulSoup, EditorJSElement, dict[Any, dict[str, Any]], Any]:
        """
            Finds inline elements by the must_have_attrs and can_have_attrs.
            Designed to be database-efficient; allowing for gathering of all data before
            making a database request.

            I.E. For a link; this would gather all page ID's and fetch them in a single query.
        """
        content = element.content
        matches: dict[Any, dict[str, Any]] = {}
        soup = bs4.BeautifulSoup(content, "html.parser")
        for key, value in self.must_have_attrs.items():
            arguments = [self.tag_name, {key: value}]
            if not value:
                def filter(item):
                    if item.has_attr(key):
                        return True
                    return False
                arguments = [filter]

            found = soup.find_all(*arguments)
            if not found:
                return None
            
            if not matches:
                matches = {
                    item: {}
                    for item in found
                }

            for item in found:
                matches[item][key] = item.get(key)

        for key, value in self.can_have_attrs.items():
            arguments = [self.tag_name, {key: value}]
            if not value:
                def filter(item):
                    if item.has_attr(key):
                        return True
                    return False
                arguments = [filter]

            for item in soup.find_all(*arguments):
                matches[item] = item.get(key)
        
        
        return (soup, element, matches, data)

class LazyModelInlineEditorJSFeature(LazyInlineEditorJSFeature):
    model = None
    chooser_class = None
    tag_name = "a"
    id_attr = "data-id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, tag_name=self.tag_name, **kwargs)
        self.must_have_attrs = self.must_have_attrs | {
            self.id_attr: None,
            f"data-{self.model._meta.model_name}": None,
            "class": f"wagtail-{self.model._meta.model_name}-link"
        }


    @cached_property
    def widget(self):
        return self.chooser_class()


    def get_id(self, item, attrs: dict[str, Any], context: dict[str, Any] = None):
        return int(attrs[self.id_attr])


    def get_config(self, context: dict[str, Any]):
        config = super().get_config() or {}
        config.setdefault("config", {})
        config["config"]["chooserId"] =\
            f"editorjs-{self.model._meta.model_name}-chooser-{context['widget']['attrs']['id']}"
        return config


    def render_template(self, context: dict[str, Any] = None):
        return self.widget.render_html(
            f"editorjs-{self.model._meta.model_name}-chooser-{context['widget']['attrs']['id']}",
            None,
            {"id": f"editorjs-{self.model._meta.model_name}-chooser-{context['widget']['attrs']['id']}"}
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

    
    def get_url(self, instance):
        return instance.url
    
    def get_full_url(self, instance, request):
        return request.build_absolute_uri(self.get_url(instance))


    def build_elements(self, inline_data: list, context: dict[str, Any] = None) -> list:
        """
            Process the bulk data; fetch all pages in one go
            and build the elements.
        """
        super().build_elements(inline_data, context=context)
        ids = []
        element_soups = []
        for data in inline_data:
            # soup: BeautifulSoup
            # element: EditorJSElement
            # matches: dict[bs4.elementType, dict[str, Any]]
            # data: dict[str, Any] # Block data.
            soup, element, matches, data = data

            # Store element and soup for later replacement of content.
            element_soups.append((soup, element))

            # Item is bs4 tag, attrs are must_have_attrs
            for (item, attrs) in matches.items():
                id = self.get_id(item, attrs, context)
                ids.append((item, id))

                # delete all attributes
                for key in list(item.attrs.keys()):
                    del item[key]
        
        # Fetch all objects
        objects = self.model.objects.in_bulk([id for item, id in ids])
        for item, id in ids:
            self.build_element(item, objects[id], context)

        # Replace the element's content with the new soup
        for soup, element in element_soups:
            element.content = soup.prettify()

    def get_css(self):
        return self.widget.media._css.get("all", []) + super().get_css()
    
    def get_js(self):
        return (self.widget.media._js or []) + super().get_js()
    
    @classmethod
    def get_test_data(cls):
        return None

            

class InlineEditorJSFeature(BaseInlineEditorJSFeature):
    """
        Builds the elements for the inline data immediately.
        Does not allow for lazy prefetching of all data.
    """

    def build_elements(self, soup: bs4.BeautifulSoup, element: EditorJSElement, matches: dict[Any, dict[str, Any]], block_data: Any, context = None):
        pass

    def parse_inline_data(self, element: EditorJSElement, data: Any, context=None) -> tuple[bs4.BeautifulSoup, EditorJSElement, dict[Any, dict[str, Any]], Any]:
        soup, element, matches, block_data = super().parse_inline_data(element, data, context)
        self.build_elements(soup=soup, element=element, matches=matches, block_data=block_data, context=context)
        element.content = soup.prettify()
        return element    
            

def get_features(features: list[str] = None):
    if not features:
        features = list(EDITOR_JS_FEATURES.keys())

    for feature in features:
        if feature not in EDITOR_JS_FEATURES:
            raise ValueError(f"Unknown feature: {feature}")

    return features

class EditorJSFeatures:
    def __init__(self):
        self.features: dict[str, Union[EditorJSFeature, EditorJSTune]] = {}
        self.inline_features: list[InlineEditorJSFeature] = []
        self.tunes_for_all: list[str] = []
        self.tunes_for_tools: defaultdict[str, list[str]] = defaultdict(list)
        self._looked_for_features = False


    def __contains__(self, tool_name: str):
        self._look_for_features()
        return tool_name in self.features


    def __getitem__(self, tool_name: str) -> Union[EditorJSFeature, EditorJSTune, InlineEditorJSFeature]:
        self._look_for_features()

        if isinstance(tool_name, BaseEditorJSFeature):
            return tool_name

        return self.features[tool_name]

    def keys(self):
        self._look_for_features()
        return self.features.keys()


    def _look_for_features(self):
        if not self._looked_for_features:
            for hook in hooks.get_hooks(REGISTER_HOOK_NAME):
                hook(self)
            self._looked_for_features = True


    def register(self, tool_name: str, feature: EditorJSFeature):
        self.features[tool_name] = feature
        if isinstance(feature, BaseInlineEditorJSFeature):
            self.inline_features.append(feature)


    def register_tune(self, tune_name: str, tool_name: str = None):
        if tool_name:
            self.tunes_for_tools[tool_name].append(tune_name)
        else:
            self.tunes_for_all.append(tune_name)


    def register_config(self, tool_name: str, config: dict):
        self._look_for_features()
        self.features[tool_name].config.update(config)


    def build_config(self, tools: list[str], context: dict[str, Any] = None):
        editorjs_config = {}
        editorjs_config_tools = {}
        self._look_for_features()

        for tool in tools:
            if tool not in self.features:
                raise ValueError(f"Unknown feature: {tool}")

            tool_mapping = self.features[tool]
            tool_config = tool_mapping.get_config(context)
            if tool_config is None:
                continue

            tool_config = copy.deepcopy(tool_config)

            if "tunes" in tool_config:
                raise ValueError(f"Tunes must be registered separately for {tool}")

            tunes = self.tunes_for_tools[tool]
            if tunes:
                tool_config["tunes"] = tunes

            editorjs_config_tools[tool] = tool_config

        if self.tunes_for_all:
            editorjs_config["tunes"] = list(
                filter(lambda tune: tune in tools, self.tunes_for_all)
            )

        editorjs_config["tools"] = editorjs_config_tools

        return editorjs_config
    

    def to_python(self, tools: list[str], data: list[dict]):
        """
            Converts the data from the editorjs format to the python format.
        """

        if isinstance(data, EditorJSValue):
            return data

        self._look_for_features()
        block_list = data.get("blocks", [])
        features = {
            tool: self.features[tool]
            for tool in tools
        }

        for i, item in enumerate(block_list):
            block_type = item.get("type")
            if block_type not in tools:
                continue

            tool_mapping = features[block_type]
            block_list[i] = tool_mapping.create_block(tools, item)

        data["blocks"] = block_list

        return EditorJSValue(
            data,
            {
                tool: self.features[tool]
                for tool in tools
            }
        )


    def prepare_value(self, tools: list[str], data: dict):
        """
            Filters out unknown features and tunes.
        """
        self._look_for_features()
        block_list = data.get("blocks", [])
        blocks = [None] * len(block_list)
        for i, item in enumerate(block_list):

            block_type = item.get("type")
            if block_type not in tools:
                continue

            tunes = item.get("tunes", {})
            if tunes:
                keys = list(tunes.keys())
                for key in keys:
                    if key not in tools:
                        del tunes[key]

            blocks[i] = item

        data["blocks"] = list(filter(None, blocks))
        return data

    def get_by_weight(self, tools: list[str]) -> OrderedDict[str, EditorJSFeature]:
        """
            Returns the tools sorted by weight.
            Items with the lowest weight are first.
        """
        self._look_for_features()
        od = OrderedDict()
        
        values = list(self.features.values())
        values.sort(key=lambda x: x.weight)
        
        for value in values:
            if value.tool_name in tools:
                od[value.tool_name] = value
        
        return od
    
    def update_config(self, tool: str, config: dict):
        self.features[tool].config.update(config)

    def validate_for_tools(self, tools: list[str], data: dict):
        """
            Validates the data for the given tools.
        """
        self._look_for_features()

        block_list = data.get("blocks", [])

        for tool in tools:
            if tool not in self.features:
                raise ValueError(f"Unknown feature: {tool}")
            
            tool_mapping = self.features[tool]

            for item in block_list:
                if isinstance(tool_mapping, EditorJSTune):
                    tunes = item.get("tunes", {})
                    tune = tunes.get(tool)
                    if tune:
                        tool_mapping.validate(tune)

                else:
                    if item["type"] == tool:
                        tool_mapping.validate(item)

        return data



EDITOR_JS_FEATURES = EditorJSFeatures()
