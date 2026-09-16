from app.services.report import build_report, report_html, report_json


def sample():
    return {
        "page_title": "Example",
        "requested_url": "https://example.com",
        "final_url": "https://example.com/",
        "request_count": 2,
        "third_party_request_count": 1,
        "failed_request_count": 0,
        "known_response_bytes": 1234,
        "requests": [{"host": "example.com", "resource_type": "document", "status": 200, "duration_ms": 10, "response_size": 1234}],
    }


def test_report_has_schema_version():
    assert build_report(sample())["schema_version"] == "1.0"


def test_json_report_is_serializable():
    output = report_json(sample())
    assert '"schema_version": "1.0"' in output


def test_html_report_escapes_untrusted_text():
    data = sample()
    data["page_title"] = '<script>alert(1)</script>'
    output = report_html(data)
    assert "<script>alert(1)</script>" not in output
    assert "&lt;script&gt;" in output
