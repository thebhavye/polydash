"""The v1 schema: validation expectations live here, not in individual rules."""
STRING = {"type": "string"}
NUMBER = {"type": "number"}
BOOLEAN = {"type": "boolean"}
STRINGS = {"type": "array", "items": STRING}
BINDING = {"type": "object", "properties": {"source": STRING}, "required": ["source"]}
LAYOUT = {
    "type": "object",
    "properties": {"direction": {"type": "string", "enum": ["row", "column"]}},
    "required": ["direction"],
}
COMMON = {"id": STRING, "type": STRING, "title": STRING}
COMPONENTS = {
    "metric": {"properties": {**COMMON, "value": NUMBER, "unit": STRING},
               "required": ["id", "type", "value"]},
    "chart": {"properties": {**COMMON, "data": BINDING, "series": STRINGS,
                              "kind": {"type": "string", "enum": ["line", "bar"]},
                              "stacked": BOOLEAN},
              "required": ["id", "type", "data", "series"]},
    "table": {"properties": {**COMMON, "data": BINDING, "columns": STRINGS,
                              "rows": {"type": "array", "items": {"type": "array", "items": NUMBER}}},
              "required": ["id", "type", "data", "columns"]},
    "filter": {"properties": {**COMMON, "options": STRINGS, "multiple": BOOLEAN},
               "required": ["id", "type", "options"]},
    "group": {"properties": {**COMMON, "layout": LAYOUT,
                              "children": {"type": "array", "items": {"type": "object"}}},
              "required": ["id", "type", "layout", "children"]},
}
DASHBOARD = {"properties": {"title": STRING, "layout": LAYOUT,
                             "theme": {"type": "string", "enum": ["light", "dark"]},
                             "components": {"type": "array", "items": {"type": "object"}}},
             "required": ["title", "layout", "components"]}
