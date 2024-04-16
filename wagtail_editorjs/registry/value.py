from typing import Any, Union, TYPE_CHECKING
import datetime

if TYPE_CHECKING:
    from .features import EditorJSFeature


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
    
    def __getitem__(self, __key: Any) -> Any:
        if isinstance(__key, int):
            return self.blocks[__key]
        
        return super().__getitem__(__key)

    def get_blocks_by_name(self, name: str) -> list["EditorJSBlock"]:
        if name not in self._features:
            return []
        
        return [
            block
            for block in self.blocks
            if block.get('type') == name
        ]
    
    def get_block_by_id(self, id: str) -> "EditorJSBlock":
        for block in self.blocks:
            if block.get("id") == id:
                return block
        return None
    
    def get_range(self, start: int, end: int) -> list["EditorJSBlock"]:
        return self["blocks"][start:end]
    
    def set_range(self, start: int, end: int, blocks: list["EditorJSBlock"]):
        b = self["blocks"]
        if start < 0:
            start = 0
        
        if end > len(b):
            end = len(b)
        
        if start > end:
            start = end
        
        if start == end:
            return
        
        b[start:end] = list(
            map(self._verify_block, blocks),
        )
        self["blocks"] = b

    def insert(self, index: int, block: "EditorJSBlock"):
        block = self._verify_block(block)        
        self.blocks.insert(index, block)

    def append(self, block: "EditorJSBlock"):
        block = self._verify_block(block)
        self.blocks.append(block)

    def _verify_block(self, block: Union["EditorJSBlock", dict]):
        if block.get("type") not in self._features:
            raise ValueError(f"Unknown feature: {block.get('type')}")
        
        if block.get("id") is None:
            raise ValueError("Block ID not set")
        
        if not isinstance(block, EditorJSBlock)\
            and isinstance(block, dict):
            
            block = self._features[block["type"]].create_block(
                list(self._features.keys()),
                block
            )

        return block
