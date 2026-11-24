"""
Pydantic schemas for KrishiSetu AI.
Covers Multimodal Leaf Diagnostics, Vernacular Speech-to-Advisory,
APMC Mandi Price Forecasting, FPO SaaS Aggregation, and Customer Discovery Evidence.
"""
from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class CropType(str, Enum):
    TOMATO = "TOMATO"
    COTTON = "COTTON"
    SOYBEAN = "SOYBEAN"
    SUGARCANE = "SUGARCANE"
    WHEAT = "WHEAT"
    PADDY = "PADDY"
    POMEGRANATE = "POMEGRANATE"
    ONION = "ONION"


class DiseaseSeverity(str, Enum):
    HEALTHY = "HEALTHY"
    EARLY_ONSET = "EARLY_ONSET"
    MODERATE = "MODERATE"
    SEVERE_BLIGHT = "SEVERE_BLIGHT"


class IndicLanguage(str, Enum):
    HINDI = "hi"
    MARATHI = "mr"
    TELUGU = "te"
    KANNADA = "kn"
    GUJARATI = "gu"
    ENGLISH = "en"


class DiagnosisRequest(BaseModel):
    crop: CropType
    image_b64: Optional[str] = None
    leaf_symptoms_description: Optional[str] = None
    language: IndicLanguage = IndicLanguage.HINDI
    location_district: str = "Nashik"
    acres_cultivated: float = 2.5


class CropDiseaseDiagnosis(BaseModel):
    diagnosis_id: str
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    crop: CropType
    detected_disease: str
    disease_scientific_name: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    severity: DiseaseSeverity
    affected_leaf_area_pct: float = Field(..., ge=0.0, le=100.0)
    biological_remedy: str
    chemical_remedy: str
    dosage_per_acre: str
    estimated_prevented_loss_inr: int
    vernacular_audio_summary: str
    audio_transcription: str


class VernacularVoiceQuery(BaseModel):
    query_id: str
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    farmer_name: str = "Ramesh Patil"
    language: IndicLanguage = IndicLanguage.MARATHI
    spoken_text: str
    detected_intent: str
    ai_response_text: str
    voice_audio_uri: str
    suggested_action: str


class MandiPriceForecast(BaseModel):
    commodity: str
    apmc_mandi_name: str
    district: str
    state: str = "Maharashtra"
    current_modal_price_per_quintal: int
    predicted_price_7d: int
    predicted_price_14d: int
    price_trend: str  # BULLISH, BEARISH, STABLE
    recommendation: str  # SELL_NOW, HOLD_FOR_PEAK, DIVERSIFY_MANDI
    arbitrage_opportunity_mandi: Optional[str] = None
    net_arbitrage_gain_per_quintal: Optional[int] = None


class CustomerInterviewRecord(BaseModel):
    interview_id: str
    interview_date: str
    farmer_or_leader_name: str
    role_or_fpo: str
    location: str
    crop_focus: str
    pain_point_summary: str
    quoted_statement: str
    willingness_to_pay: str
    validation_status: str = "VERIFIED_CALL_NOTES"


class FPOSubscriptionPlan(BaseModel):
    fpo_id: str
    fpo_name: str
    registered_farmers_count: int
    active_acres: int
    monthly_saas_tier: str = "ENTERPRISE_FPO"
    subscription_fee_inr_month: int = 4999
    features_unlocked: List[str]
    current_month_pesticide_savings_inr: int
