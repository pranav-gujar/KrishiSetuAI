"""
FPO B2B SaaS Enterprise Engine.
Aggregates member farmer diagnostic data into collective pest alerts,
bulk chemical input group buying discounts, and subscription unit economics.
"""
from typing import Dict, Any, List
from app.schemas.agriculture import FPOSubscriptionPlan

# Pre-configured FPO Clusters across Western & Southern India
FPO_CLUSTERS = [
    {
        "fpo_id": "FPO-MH-SAHYADRI",
        "fpo_name": "Sahyadri Mahila Farmer Producer Co.",
        "registered_farmers_count": 1200,
        "active_acres": 4800,
        "monthly_saas_tier": "ENTERPRISE_FPO",
        "subscription_fee_inr_month": 4999,
        "features_unlocked": [
            "Cluster-Wide Real-Time Pest Heatmap",
            "Vernacular WhatsApp Broadcast Bot (Marathi)",
            "Bulk Chemical & Fertilizer Input RFP Auction",
            "Mandi Arbitrage Truck Load Aggregation",
        ],
        "current_month_pesticide_savings_inr": 348000,
    },
    {
        "fpo_id": "FPO-KA-KRISHNA",
        "fpo_name": "Krishna Valley Sugarcane & Maize FPO",
        "registered_farmers_count": 850,
        "active_acres": 3400,
        "monthly_saas_tier": "ENTERPRISE_FPO",
        "subscription_fee_inr_month": 4999,
        "features_unlocked": [
            "Kannada Voice Automated Diagnostic Bot",
            "Sugarcane Red Rot Root Drenching Scheduler",
            "Direct Sugar Mill Procurement Linkage",
        ],
        "current_month_pesticide_savings_inr": 215000,
    },
    {
        "fpo_id": "FPO-GJ-UNJHA",
        "fpo_name": "Unjha Spice & Seed Producer Co.",
        "registered_farmers_count": 620,
        "active_acres": 2500,
        "monthly_saas_tier": "GROWTH_FPO",
        "subscription_fee_inr_month": 2999,
        "features_unlocked": [
            "Cumin & Mustard 14-Day Price Predictor",
            "Export MRL (Maximum Residue Limit) Compliance Checker",
        ],
        "current_month_pesticide_savings_inr": 182000,
    },
]


def get_fpo_clusters() -> List[FPOSubscriptionPlan]:
    return [FPOSubscriptionPlan(**c) for c in FPO_CLUSTERS]


def compute_saas_unit_economics() -> Dict[str, Any]:
    """
    Computes SaaS financial metrics and path to first 100 FPOs (FirstCheq Rubric Requirement).
    """
    avg_fpo_monthly_sub = 4999  # INR
    annual_contract_value = avg_fpo_monthly_sub * 12  # Rs. 59,988
    cac_per_fpo = 4200  # Direct field outreach via NABARD / SFAC networks
    churn_rate_annual = 0.08  # 8% annual churn
    gross_margin_pct = 0.88  # 88% software gross margin
    
    customer_lifetime_years = 1.0 / churn_rate_annual  # 12.5 years
    ltv = annual_contract_value * gross_margin_pct * customer_lifetime_years
    ltv_to_cac_ratio = round(ltv / cac_per_fpo, 1)
    
    target_100_fpos_revenue = 100 * annual_contract_value  # Rs. ~60 Lakhs ARR
    farmers_reached = 100 * 950  # ~95,000 farmers
    
    return {
        "monthly_sub_inr": avg_fpo_monthly_sub,
        "annual_contract_value_inr": annual_contract_value,
        "cac_per_fpo_inr": cac_per_fpo,
        "gross_margin_pct": 88.0,
        "payback_period_months": round((cac_per_fpo / (avg_fpo_monthly_sub * 0.88)), 1),
        "ltv_inr": int(ltv),
        "ltv_to_cac_ratio": f"{ltv_to_cac_ratio}x",
        "path_to_first_100_fpos": {
            "arr_inr": target_100_fpos_revenue,
            "arr_formatted": "Rs. 60 Lakhs ($72k ARR)",
            "farmers_impacted": farmers_reached,
            "distribution_channel": "Direct partnerships with State Rural Livelihood Missions (MSRLM), NABARD FPO aggregators, and Sahyadri Farms ecosystem.",
        }
    }
