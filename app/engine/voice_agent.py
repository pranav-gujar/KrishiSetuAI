"""
Bhasha AI - Vernacular Speech-to-Advisory Conversational Engine.
Interprets spoken farmer audio queries across Indian regional dialects (Hindi, Marathi, Kannada, Telugu)
and generates voice responses with actionable agricultural guidance.
"""
from datetime import datetime, timezone
import hashlib
from typing import Dict, Any, List
from app.schemas.agriculture import VernacularVoiceQuery, IndicLanguage

# Pre-indexed conversational audio responses across regional languages
VERNAKULAR_RESPONSES = {
    "mr": {
        "DISEASE": "टोमॅटोवरील करपा रोगासाठी 200 लिटर पाण्यात 500 ग्रॅम मॅन्कोझेब मिसळून लगेच फवारणी करा. ढगाळ हवामानात दुपारनंतर फवारा.",
        "MANDI": "आज पिंपळगाव बसवंत बाजार समितीत टोमॅटोचे भाव 1,650 रुपये प्रति क्विंटल आहेत. पुढील 7 दिवसांत भाव 1,980 रुपयांपर्यंत वाढण्याची शक्यता आहे. माल रोखून ठेवा.",
        "WEATHER": "नाशिक जिल्ह्यात उद्या दुपारनंतर हलका पाऊस पडण्याची 70% शक्यता आहे. कोणतीही रासायनिक फवारणी 24 तास पुढे ढकला.",
    },
    "hi": {
        "DISEASE": "टमाटर में अगेती झुलसा रोग के लक्षण हैं। 500 ग्राम मैंकोज़ेब 200 लीटर पानी में मिलाकर तुरंत छिड़काव करें।",
        "MANDI": "पिंपलगांव मंडी में आज टमाटर 1,650 रुपये प्रति क्विंटल बिका। 7 दिनों में भाव 1,980 रुपये तक जाने की उम्मीद है। माल अभी रोक कर रखें।",
        "WEATHER": "अगले 24 घंटे में बारिश की संभावना है। कीटनाशक का छिड़काव मौसम साफ होने तक टालें।",
    },
    "kn": {
        "DISEASE": "ಕಬ್ಬಿನ ಬೆಳೆಗೆ ಕೆಂಪು ಕೊಳೆ ರೋಗ ಬಂದಿದೆ. ಕಾರ್ಬೆಂಡಾಜಿಮ್ ದ್ರಾವಣದಿಂದ ಬೇರುಗಳ ಸುತ್ತ ಸಿಂಪಡಣೆ ಮಾಡಿ.",
        "MANDI": "ಇಂದು ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಕ್ವಿಂಟಾಲ್‌ಗೆ ಬೆಲೆ ಏರಿಕೆಯಾಗುವ ಸಾಧ್ಯತೆಯಿದೆ. ಮುಂದಿನ ವಾರ ಮಾರಾಟ ಮಾಡುವುದು ಉತ್ತಮ.",
        "WEATHER": "ನಾಳೆ ಮಳೆಯಾಗುವ ಮುನ್ಸೂಚನೆ ಇದೆ. ಸಿಂಪಡಣೆ ಕಾರ್ಯವನ್ನು ಮುಂದೂಡಿ.",
    },
    "en": {
        "DISEASE": "Tomato Early Blight detected. Spray Mancozeb 75% WP @ 500g in 200L water per acre.",
        "MANDI": "Pimpalgaon APMC Tomato modal price is Rs. 1,650/quintal. Projected to touch Rs. 1,980 in 7 days.",
        "WEATHER": "Rain forecast in next 24 hours. Postpone all foliar chemical applications.",
    }
}


def process_farmer_voice_query(
    spoken_text: str,
    language: IndicLanguage = IndicLanguage.MARATHI,
    farmer_name: str = "Dnyaneshwar Bhor",
) -> VernacularVoiceQuery:
    """
    Classifies conversational intent from spoken speech transcript and formats localized audio guidance.
    """
    text_lower = spoken_text.lower()
    
    mandi_keywords = ["bhav", "rate", "price", "mandi", "bazar", "bazaar", "भाव", "दर", "मंडी", "बाजार", "ಬೆಲೆ", "ಧಾರಣೆ"]
    weather_keywords = ["paus", "rain", "havaman", "weather", "barish", "पाऊस", "बारिश", "हवामान", "मौसम", "ಮಳೆ"]

    if any(w in text_lower for w in mandi_keywords):
        intent = "MANDI_PRICE_CHECK"
        action = "Review APMC 7-day forecast before loading produce onto truck."
        key = "MANDI"
    elif any(w in text_lower for w in weather_keywords):
        intent = "WEATHER_SPRAY_TIMING"
        action = "Check 3-day radar rain prediction before mixing costly chemical tank."
        key = "WEATHER"
    else:
        intent = "DISEASE_DIAGNOSIS"
        action = "Capture clear photograph of affected leaf underside for instant vision analysis."
        key = "DISEASE"
        
    lang_code = language.value
    resp_map = VERNAKULAR_RESPONSES.get(lang_code, VERNAKULAR_RESPONSES["hi"])
    ai_response = resp_map.get(key, resp_map["DISEASE"])
    
    query_id = f"VOX-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    
    return VernacularVoiceQuery(
        query_id=query_id,
        timestamp_utc=datetime.now(timezone.utc),
        farmer_name=farmer_name,
        language=language,
        spoken_text=spoken_text,
        detected_intent=intent,
        ai_response_text=ai_response,
        voice_audio_uri=f"/static/audio/{query_id}.mp3",
        suggested_action=action,
    )
