"""Source-aware front ends. Neither loader knows component property types."""
import json
import math
import re
from pathlib import Path

from .model import Dashboard, Diagnostic, Span, pointer


class ParseFailure(Exception):
    def __init__(self, category, message, path, span):
        self.diagnostic = Diagnostic(category, "error", message, pointer(path), span)


class Source:
    def __init__(self, text, filename):
        self.text, self.filename, self.spans = text, filename, {}

    def span(self, offset):
        line = self.text.count("\n", 0, offset) + 1
        start = self.text.rfind("\n", 0, offset) + 1
        lines = self.text.split("\n")
        return Span(self.filename, line, offset - start + 1, lines[line - 1].rstrip("\r"))

    def fail(self, category, message, path=(), offset=0):
        raise ParseFailure(category, message, path, self.span(offset))


class JsonLoader(Source):
    def load(self):
        self.offset = 0
        decoder = json.JSONDecoder()

        def skip():
            match = re.match(r"[ \t\r\n]*", self.text[self.offset:])
            self.offset += match.end()

        def value(path):
            skip()
            self.spans[path] = self.span(self.offset)
            char = self.text[self.offset:self.offset + 1]
            if char in ("{", "["):
                is_object = char == "{"
                result = {} if is_object else []
                end = "}" if is_object else "]"
                self.offset += 1
                skip()
                if self.text[self.offset:self.offset + 1] == end:
                    self.offset += 1
                    return result
                while True:
                    key = len(result)
                    if is_object:
                        skip()
                        key_offset = self.offset
                        if self.text[self.offset:self.offset + 1] != '"':
                            self.fail("PD0001", "Expected a quoted object key", path, self.offset)
                        key, self.offset = decoder.raw_decode(self.text, self.offset)
                        if key in result:
                            self.fail("PD0001", "Duplicate object key", path + (key,), key_offset)
                        skip()
                        if self.text[self.offset:self.offset + 1] != ":":
                            self.fail("PD0001", "Expected ':'", path, self.offset)
                        self.offset += 1
                    item = value(path + (key,))
                    if is_object:
                        result[key] = item
                    else:
                        result.append(item)
                    skip()
                    token = self.text[self.offset:self.offset + 1]
                    self.offset += 1
                    if token == end:
                        return result
                    if token != ",":
                        self.fail("PD0001", f"Expected ',' or '{end}'", path, self.offset - 1)
            item, self.offset = decoder.raw_decode(self.text, self.offset)
            if isinstance(item, float) and not math.isfinite(item):
                self.fail("PD0001", "Numbers must be finite", path, self.offset)
            return item

        try:
            data = value(())
            skip()
            if self.offset != len(self.text):
                self.fail("PD0001", "Unexpected trailing input", offset=self.offset)
        except json.JSONDecodeError as error:
            self.fail("PD0001", error.msg, offset=error.pos)
        return finish(data, self.spans)


class YamlLoader(Source):
    def load(self):
        import yaml
        from yaml.nodes import MappingNode, ScalarNode, SequenceNode
        try:
            # Reject aliases before composition (also avoids recursive/expanding graphs).
            for token in yaml.scan(self.text):
                if isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken, yaml.tokens.TagToken)):
                    self.fail("PD0003", "YAML anchors, aliases and explicit tags are unsupported",
                              offset=token.start_mark.index)
            loader = yaml.SafeLoader(self.text)
            try:
                root = loader.get_single_node()

                def convert(node, path):
                    self.spans[path] = self.span(node.start_mark.index)
                    if isinstance(node, MappingNode):
                        result = {}
                        for key, val in node.value:
                            if not isinstance(key, ScalarNode) or key.tag != "tag:yaml.org,2002:str":
                                self.fail("PD0003", "Mapping keys must be strings", path, key.start_mark.index)
                            if key.value in result:
                                self.fail("PD0001", "Duplicate object key", path + (key.value,), key.start_mark.index)
                            result[key.value] = convert(val, path + (key.value,))
                        return result
                    if isinstance(node, SequenceNode):
                        return [convert(child, path + (i,)) for i, child in enumerate(node.value)]
                    if node.tag not in {"tag:yaml.org,2002:" + t for t in ("str", "int", "float", "bool", "null")}:
                        self.fail("PD0003", "Unsupported YAML scalar type; quote this value", path, node.start_mark.index)
                    result = loader.construct_object(node)
                    if isinstance(result, float) and not math.isfinite(result):
                        self.fail("PD0003", "Numbers must be finite", path, node.start_mark.index)
                    return result

                if root is None:
                    self.fail("PD0002", "Expected dashboard object")
                data = convert(root, ())
            finally:
                loader.dispose()
        except yaml.YAMLError as error:
            mark = getattr(error, "problem_mark", None)
            self.fail("PD0001", getattr(error, "problem", None) or str(error),
                      offset=mark.index if mark else 0)
        return finish(data, self.spans)


def finish(data, spans):
    def shape(value, expected, path):
        if not isinstance(value, expected):
            raise ParseFailure("PD0002", f"Expected {expected.__name__}", path, spans[path])

    shape(data, dict, ())

    def components(items, path):
        shape(items, list, path)
        for i, component in enumerate(items):
            here = path + (i,)
            shape(component, dict, here)
            if "layout" in component:
                shape(component["layout"], dict, here + ("layout",))
            if "children" in component:
                components(component["children"], here + ("children",))

    if "layout" in data:
        shape(data["layout"], dict, ("layout",))
    if "components" in data:
        components(data["components"], ("components",))
    return Dashboard(data, spans)


LOADERS = {".json": JsonLoader, ".yaml": YamlLoader, ".yml": YamlLoader}


def load(text, filename):
    loader = LOADERS.get(Path(filename).suffix.lower())
    if loader is None:
        raise ParseFailure("PD0003", "Expected .json, .yaml or .yml", (), Source(text, filename).span(0))
    return loader(text, filename).load()
