"""
    This module defines mappings from tools to the editorjs javascript side.
"""

from collections import defaultdict
from typing import Any, Union
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
    def __init__(self, tool_name: str, klass: str, js: Union[str, list[str]] = None, css: Union[str, list[str]] = None, include_template: str = None, config: dict = None, **kwargs):
        
        self.tool_name = tool_name
        self.klass = klass
        self.js = js or []
        self.css = css or []
        self.config = config or dict()
        self.kwargs = kwargs
        self.include_template = include_template

    def __repr__(self):
        return f"<EditorJSFeature \"{self.tool_name}\">"

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


class EditorJSFeature(BaseEditorJSFeature):
    def validate(self, data: Any):
        if not data:
            return
        
        if "data" not in data:
            raise ValueError("Invalid data format")
    
    def render_block_data(self, block: EditorJSBlock) -> "EditorJSElement":
        return EditorJSElement(
            "div",
            block["data"].get("text")
        )


class EditorJSTune(BaseEditorJSFeature):
    """
        Works mostly like EditorJSFeature, but is used for tunes.
        Handles validation differently.
    """

    def tune_element(self, element: "EditorJSElement", tune_value: Any) -> "EditorJSElement":
        return element


class InlineEditorJSFeature(BaseEditorJSFeature):
    def __init__(self, tool_name: str, klass: str, tag_name: str, must_have_attrs: dict = None, can_have_attrs: dict = None, js: Union[str, list[str]] = None, css: Union[str, list[str]] = None, include_template: str = None, config: dict = None, **kwargs):
        super().__init__(tool_name, klass, js, css, include_template, config, **kwargs)
        self.tag_name = tag_name
        self.must_have_attrs = must_have_attrs or {}
        self.can_have_attrs = can_have_attrs or {}


    def is_inline(self):
        return True
    

    def build_element(self, soup, element: EditorJSElement, matches: dict[str, Any], block_data):
        pass
    

    def parse_inline_data(self, element: EditorJSElement, data: Any) -> EditorJSElement:
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
                return element
            
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
        
        self.build_element(soup=soup, element=element, matches=matches, block_data=data)
        content = soup.prettify()
        element.content = content
        return element


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


    def __getitem__(self, tool_name: str) -> EditorJSFeature:
        self._look_for_features()
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
        if isinstance(feature, InlineEditorJSFeature):
            self.inline_features.append(feature)


    def register_tune(self, tune_name: str, tool_name: str = None):
        if tool_name:
            self.tunes_for_tools[tool_name].append(tune_name)
        else:
            self.tunes_for_all.append(tune_name)


    def register_config(self, tool_name: str, config: dict):
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
