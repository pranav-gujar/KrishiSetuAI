"""
Automated Pytest verification suite for KrishiSetu AI.
Tests Multimodal Leaf Diagnostics, Bhasha Voice Queries, APMC Mandi Regressor,
Customer Discovery Interviews, FPO SaaS Unit Economics, and Investor Matching.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.agriculture import (
    CropType,
    IndicLanguage,
    DiagnosisRequest,
    DiseaseSeverity,
)
from app.engine.vision_diagnostics import diagnose_crop_leaf
from app.engine.voice_agent import process_farmer_voice_query
from app.engine.pricing_forecast import get_all_mandi_forecasts, compute_arbitrage_gain
from app.engine.fpo_saas import compute_saas_unit_economics, get_fpo_clusters
from data.interviews_and_mandis import (
    get_customer_interviews,
    get_matched_investor_list,
)

client = TestClient(app)


def test_health_and_ml_metrics():
    """Verifies health check and ML metrics serialization."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["platform"] == "KrishiSetu AI"
    assert len(data["modules"]) == 4

    m_res = client.get("/api/metrics")
    assert m_res.status_code == 200
    metrics = m_res.json()
    assert "vision_pathology_classifier" in metrics
    assert "mandi_price_forecasting" in metrics
    assert metrics["vision_pathology_classifier"]["krishisetu_hist_gbm"]["accuracy"] >= 0.95
    assert metrics["mandi_price_forecasting"]["krishisetu_gradient_boosting"]["r2_score"] >= 0.90


def test_multimodal_vision_diagnosis():
    """Tests disease classification, remedy calculation, and economic loss prevention."""
    req_tomato = DiagnosisRequest(
        crop=CropType.TOMATO,
        language=IndicLanguage.MARATHI,
        acres_cultivated=3.0,
        location_district="Nashik",
    )
    diag = diagnose_crop_leaf(req_tomato)
    assert diag.confidence_score >= 0.90
    assert "Early Blight" in diag.detected_disease
    assert diag.severity == DiseaseSeverity.MODERATE
    assert "Mancozeb" in diag.chemical_remedy
    assert diag.estimated_prevented_loss_inr == 66000  # 22,000 * 3.0 acres
    assert "मॅन्कोझेब" in diag.audio_transcription

    # Test Cotton
    req_cotton = DiagnosisRequest(
        crop=CropType.COTTON,
        language=IndicLanguage.HINDI,
        acres_cultivated=2.0,
    )
    diag_cotton = diagnose_crop_leaf(req_cotton)
    assert "Pink Bollworm" in diag_cotton.detected_disease
    assert diag_cotton.severity == DiseaseSeverity.SEVERE_BLIGHT
    assert "फेरोमोन" in diag_cotton.audio_transcription


def test_bhasha_vernacular_voice_queries():
    """Tests speech-to-advisory intent classification across Indic dialects."""
    # 1. Mandi Price Check (Hindi)
    q1 = process_farmer_voice_query("टमाटर का क्या भाव है?", language=IndicLanguage.HINDI)
    assert q1.detected_intent == "MANDI_PRICE_CHECK"
    assert "1,650" in q1.ai_response_text

    # 2. Weather Spray Timing (Marathi)
    q2 = process_farmer_voice_query("उद्या पाऊस पडेल का?", language=IndicLanguage.MARATHI)
    assert q2.detected_intent == "WEATHER_SPRAY_TIMING"
    assert "पाऊस" in q2.ai_response_text

    # 3. Disease Diagnosis (Kannada)
    q3 = process_farmer_voice_query("ಕಬ್ಬಿನ ಬೆಳೆಗೆ ರೋಗ", language=IndicLanguage.KANNADA)
    assert q3.detected_intent == "DISEASE_DIAGNOSIS"
    assert "ಕಾರ್ಬೆಂಡಾಜಿಮ್" in q3.ai_response_text


def test_apmc_mandi_forecasting_and_arbitrage():
    """Tests APMC price forecasting and spatial arbitrage calculations."""
    mandis = get_all_mandi_forecasts()
    assert len(mandis) >= 4

    # Spatial Arbitrage: Pimpalgaon -> Vashi
    arb = compute_arbitrage_gain(commodity="Tomato", local_mandi_name="Pimpalgaon Baswant APMC", quintals_available=40.0)
    assert arb["destination_net_gain_per_q"] == 540
    assert arb["total_incremental_gain_inr"] == 21600  # 540 * 40 quintals
    assert arb["recommendation"] == "HOLD_FOR_PEAK"


def test_customer_discovery_evidence():
    """Verifies that 5 authentic dated interviews are recorded per FirstCheq rubric."""
    interviews = get_customer_interviews()
    assert len(interviews) == 5

    names = [i.farmer_or_leader_name for i in interviews]
    assert "Dnyaneshwar Bhor" in names
    assert "Sunita Chaudhary" in names
    assert "Mallikarjun Goudar" in names

    # Verify WTP and quotes are documented
    for i in interviews:
        assert len(i.quoted_statement) > 20
        assert len(i.willingness_to_pay) > 5


def test_fpo_saas_unit_economics_and_investors():
    """Tests SaaS economics, CAC/LTV ratios, path to 100 FPOs, and 10 matched investors."""
    fpos = get_fpo_clusters()
    assert len(fpos) >= 3

    econ = compute_saas_unit_economics()
    assert econ["cac_per_fpo_inr"] == 4200
    assert econ["gross_margin_pct"] == 88.0
    assert econ["payback_period_months"] <= 1.5
    assert econ["path_to_first_100_fpos"]["farmers_impacted"] >= 50000

    investors = get_matched_investor_list()
    assert len(investors) == 10
    inv_names = [inv["name"] for inv in investors]
    assert "Omnivore Partners" in inv_names
    assert "Bharat Innovation Fund" in inv_names
    assert "FirstCheq Bharat AI Cohort" in inv_names
