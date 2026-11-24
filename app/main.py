"""
FastAPI application for KrishiSetu AI.
Powers Multimodal Crop Disease Diagnostics, Vernacular Voice Queries,
APMC Mandi Price Forecasting, FPO Cluster SaaS, and Customer Discovery Evidence.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import json
from typing import Dict, Any, List

from app.schemas.agriculture import (
    DiagnosisRequest,
    CropDiseaseDiagnosis,
    VernacularVoiceQuery,
    MandiPriceForecast,
    IndicLanguage,
)
from app.engine.vision_diagnostics import diagnose_crop_leaf
from app.engine.voice_agent import process_farmer_voice_query
from app.engine.pricing_forecast import get_all_mandi_forecasts, compute_arbitrage_gain
from app.engine.fpo_saas import get_fpo_clusters, compute_saas_unit_economics
from data.interviews_and_mandis import (
    get_customer_interviews,
    get_matched_investor_list,
    CROP_DISEASE_DB,
)

app = FastAPI(
    title="KrishiSetu AI API",
    description="Multimodal Vernacular Crop Health & APMC Market Intelligence Platform for FirstCheq Build with AI Challenge",
    version="1.0.0",
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "ml", "artifacts")


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "platform": "KrishiSetu AI",
        "track": "first_cheq_build_with_ai",
        "partners": ["FirstCheq", "E-Cell IIT Bombay"],
        "modules": [
            "Multimodal Edge Vision Leaf Diagnostics",
            "Bhasha AI Vernacular Speech-to-Advisory",
            "Agmarknet APMC Mandi Price Regressor",
            "FPO B2B SaaS Aggregator",
        ]
    }


@app.post("/api/diagnose")
def diagnose_crop(req: DiagnosisRequest):
    return diagnose_crop_leaf(req).model_dump()


@app.post("/api/voice/query")
def voice_query(payload: Dict[str, Any]):
    spoken_text = payload.get("spoken_text", "माझ्या टोमॅटो पिकावर करपा आला आहे काय करू?")
    lang_val = payload.get("language", "mr")
    try:
        lang = IndicLanguage(lang_val)
    except ValueError:
        lang = IndicLanguage.MARATHI
    name = payload.get("farmer_name", "Dnyaneshwar Bhor")
    return process_farmer_voice_query(spoken_text, language=lang, farmer_name=name).model_dump()


@app.get("/api/mandis")
def list_mandis():
    return [m.model_dump() for m in get_all_mandi_forecasts()]


@app.post("/api/mandis/arbitrage")
def check_arbitrage(payload: Dict[str, Any]):
    commodity = payload.get("commodity", "Tomato")
    local_mandi = payload.get("local_mandi", "Pimpalgaon Baswant APMC")
    quintals = float(payload.get("quintals", 50.0))
    return compute_arbitrage_gain(commodity, local_mandi, quintals_available=quintals)


@app.get("/api/fpos")
def list_fpos():
    return {
        "fpos": [f.model_dump() for f in get_fpo_clusters()],
        "unit_economics": compute_saas_unit_economics(),
    }


@app.get("/api/interviews")
def list_interviews():
    return [i.model_dump() for i in get_customer_interviews()]


@app.get("/api/investors")
def list_investors():
    return get_matched_investor_list()


@app.get("/api/metrics")
def get_ml_metrics():
    metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(status_code=404, detail="ML metrics not yet generated")
    with open(metrics_path, "r") as f:
        return json.load(f)


if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "KrishiSetu AI API online. Mount index.html in app/static."}
