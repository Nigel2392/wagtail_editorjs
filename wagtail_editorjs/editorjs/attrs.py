from typing import Any, Union


class EditorJSElementAttribute:
    def __init__(self, value: Union[str, list[str]], delimiter: str = " "):
        if not isinstance(value, (list, dict)):
            value = [value]

        self.value = value
        self.delimiter = delimiter

    def __eq__(self, other):
        if isinstance(other, EditorJSElementAttribute):
            return self.value == other.value
        
        if isinstance(other, list):
            for item in other:
                if item not in self.value:
                    return False
            return True
        return False

    def extend(self, value: Any):
        if isinstance(value, list):
            self.value.extend(value)
        else:
            self.value.append(value)

    def __str__(self):
        return self.delimiter.join([str(item) for item in self.value])
    

class EditorJSStyleAttribute(EditorJSElementAttribute):
    def __init__(self, value: dict):
        super().__init__(value, ";")

    def __repr__(self):
        return f"EditorJSStyleAttribute({self.value})"

    def __eq__(self, other):
        if isinstance(other, EditorJSStyleAttribute):
            return self.value == other.value
        
        if isinstance(other, dict):
            return self.value == other
        
        if isinstance(other, str):
            try:
                key, value = other.split(":")
                return self.value.get(key) == value.strip()
            except ValueError:
                return False
        return False

    def extend(self, value: dict = None, **kwargs):
        if value:
            if not isinstance(value, dict):
                raise ValueError("Value must be a dictionary")
            self.value.update(value)

        self.value.update(kwargs)

    def __str__(self):
        return self.delimiter.join([f'{key}: {value}' for key, value in self.value.items()])
