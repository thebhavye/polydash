"""Small static HTML prototype for an already validated Dashboard."""

from html import escape

from .model import Dashboard


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _component(component: dict) -> str:
    kind = component["type"]
    title = component.get("title") or component["id"]
    heading = f"<h2>{_text(title)}</h2>"

    if kind == "group":
        children = "\n".join(_component(child) for child in component["children"])
        direction = component["layout"]["direction"]
        return f'<section class="card group"><h2>{_text(title)}</h2><div class="grid {direction}">{children}</div></section>'

    if kind == "metric":
        unit = f' <span class="unit">{_text(component["unit"])}</span>' if "unit" in component else ""
        body = f'<p class="value">{_text(component["value"])}{unit}</p>'
    elif kind == "table":
        columns = component["columns"]
        header = "".join(f"<th scope=\"col\">{_text(name)}</th>" for name in columns)
        rows = "".join(
            "<tr>" + "".join(f"<td>{_text(value)}</td>" for value in row) + "</tr>"
            for row in component.get("rows", [])
        )
        body = (f'<div class="table-wrap"><table><thead><tr>{header}</tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')
        if "rows" not in component:
            body += '<p class="note">No rows supplied in this configuration.</p>'
    elif kind == "filter":
        options = "".join(f"<option>{_text(value)}</option>" for value in component["options"])
        multiple = " multiple" if component.get("multiple", False) else ""
        body = f'<label>{_text(title)}<select{multiple}>{options}</select></label>'
        heading = ""
    elif kind == "chart":
        source = component["data"]["source"]
        series = ", ".join(component["series"])
        body = (f'<div class="chart-placeholder" role="note">Chart data is not loaded in this static preview.'
                f'<br><small>Source: {_text(source)} · Series: {_text(series)}</small></div>')
    else:
        raise ValueError(f"Unsupported validated component type: {kind}")

    return f'<section class="card {kind}">{heading}{body}</section>'


def generate_html(ir: Dashboard) -> str:
    """Return one portable, dependency-free HTML file; callers gate on validation."""
    config = ir.config
    title = _text(config["title"])
    theme = config.get("theme", "light")
    direction = config["layout"]["direction"]
    components = "\n".join(_component(item) for item in config["components"])
    return f"""<!doctype html>
<html lang="en" data-theme="{theme}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | PolyDash</title>
<style>
:root {{ font-family: system-ui, sans-serif; color-scheme: light; --bg:#f3f6fb; --surface:#fff; --ink:#172338; --muted:#536178; --border:#d9e2ed; --accent:#2458b8; }}
[data-theme="dark"] {{ color-scheme: dark; --bg:#101827; --surface:#1b2940; --ink:#eef4ff; --muted:#b9c7db; --border:#3d5069; --accent:#8bb6ff; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:var(--bg); color:var(--ink); }}
main {{ max-width:1100px; margin:auto; padding:2rem 1rem 4rem; }}
header {{ margin-bottom:1.5rem; }} h1 {{ margin:0; font-size:clamp(1.8rem,4vw,2.8rem); }}
.eyebrow {{ color:var(--accent); font-weight:700; letter-spacing:.1em; text-transform:uppercase; font-size:.75rem; }}
.grid {{ display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr)); align-items:start; }}
.grid.column {{ grid-template-columns:1fr; }} .card {{ background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:1.25rem; min-width:0; box-shadow:0 4px 18px #0000000a; }}
.card h2 {{ font-size:1rem; margin:0 0 1rem; }} .value {{ font-size:2.4rem; font-weight:750; margin:.2rem 0; color:var(--accent); }} .unit {{ font-size:1rem; color:var(--muted); }}
.group {{ grid-column:1/-1; }} .table-wrap {{ overflow-x:auto; }} table {{ border-collapse:collapse; width:100%; text-align:left; }} th,td {{ padding:.65rem; border-bottom:1px solid var(--border); }}
th,.note,small {{ color:var(--muted); }} label {{ display:grid; gap:.6rem; font-weight:650; }} select {{ width:100%; padding:.6rem; border:1px solid var(--border); border-radius:8px; background:var(--surface); color:var(--ink); }}
.chart-placeholder {{ min-height:140px; display:grid; place-content:center; text-align:center; border:1px dashed var(--border); border-radius:10px; color:var(--muted); line-height:1.8; }}
</style>
</head>
<body><main><header><p class="eyebrow">PolyDash preview</p><h1>{title}</h1></header>
<div class="grid {direction}">{components}</div>
</main></body></html>
"""
