"""
    This module defines mappings from tools to the editorjs javascript side.
"""

from collections import defaultdict, OrderedDict
from typing import Any, Union
from wagtail import hooks

import copy
from ..hooks import (
    REGISTER_HOOK_NAME,
)
from .value import (
    EditorJSValue,
)

from .features import (
    BaseEditorJSFeature,
    EditorJSFeature,
    EditorJSTune,
    InlineEditorJSFeature,
)


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
        if isinstance(feature, InlineEditorJSFeature):
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



