from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl

from app.services.analyzer import analyze_url
from app.services.report import report_html, report_json

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Internet X-Ray",
    version="0.3.0",
    description="Analyze the hidden network activity behind a web page.",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnalyzeRequest(BaseModel):
    url: HttpUrl


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(payload: AnalyzeRequest) -> dict:
    try:
        return await analyze_url(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The target page could not be analyzed. Check the URL and try again.",
        ) from exc


@app.post("/api/report/json")
async def export_json(payload: dict) -> Response:
    return Response(report_json(payload), media_type="application/json")


@app.post("/api/report/html")
async def export_html(payload: dict) -> Response:
    return Response(report_html(payload), media_type="text/html")
