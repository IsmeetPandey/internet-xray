from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from typing import Any


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    """Return a compact, stable report envelope for export and future storage."""
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def report_json(data: dict[str, Any]) -> str:
    return json.dumps(build_report(data), indent=2, sort_keys=True)


def report_html(data: dict[str, Any]) -> str:
    report = build_report(data)
    title = escape(str(data.get("page_title") or "Internet X-Ray report"))
    requested = escape(str(data.get("requested_url", "")))
    final_url = escape(str(data.get("final_url", "")))
    rows = "".join(
        f"<tr><td>{escape(str(item.get('host', '')))}</td>"
        f"<td>{escape(str(item.get('resource_type', '')))}</td>"
        f"<td>{escape(str(item.get('status', '')))}</td>"
        f"<td>{escape(str(item.get('duration_ms', '')))}</td>"
        f"<td>{escape(str(item.get('response_size', '')))}</td></tr>"
        for item in data.get("requests", [])[:200]
    )
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{title} — Internet X-Ray</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1100px;margin:40px auto;padding:0 20px;color:#18202a}}code{{word-break:break-all}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:left}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.card{{padding:16px;background:#f4f6f8;border-radius:10px}}small{{color:#667}}@media(max-width:700px){{.grid{{grid-template-columns:1fr 1fr}}}}</style>
</head><body><h1>Internet X-Ray</h1><h2>{title}</h2><p><small>Requested:</small> <code>{requested}</code><br><small>Final:</small> <code>{final_url}</code></p>
<div class=\"grid\">{''.join(f'<div class=\"card\"><small>{escape(str(k))}</small><br><strong>{escape(str(v))}</strong></div>' for k,v in (("Requests",data.get("request_count",0)), ("Third-party",data.get("third_party_request_count",0)), ("Failed",data.get("failed_request_count",0)), ("Known bytes",data.get("known_response_bytes",0))))}</div>
<h2>Requests</h2><table><thead><tr><th>Host</th><th>Type</th><th>Status</th><th>Duration</th><th>Bytes</th></tr></thead><tbody>{rows}</tbody></table>
<p><small>Schema {escape(str(report["schema_version"]))} · Generated {escape(str(report["generated_at"]))}</small></p></body></html>"""
