"""
AgroSustain — Economics Calculator
Estimates crop yield, investment, and profit based on farm area and crop type.
"""

# ── Crop Financial Profiles ───────────────────────────────────────────────────
# Values are approximate averages for Indian agriculture
# yield_per_hectare: metric tons/hectare
# price_per_ton_inr: INR
# investment_per_hectare: INR (seed, fertilizer, irrigation, labor)

CROP_PROFILES = {
    "rice":         {"yield_per_ha": 2.5,  "price_per_ton": 20000, "invest_per_ha": 35000},
    "maize":        {"yield_per_ha": 3.0,  "price_per_ton": 16000, "invest_per_ha": 28000},
    "chickpea":     {"yield_per_ha": 1.2,  "price_per_ton": 55000, "invest_per_ha": 22000},
    "kidneybeans":  {"yield_per_ha": 1.0,  "price_per_ton": 60000, "invest_per_ha": 25000},
    "pigeonpeas":   {"yield_per_ha": 1.1,  "price_per_ton": 58000, "invest_per_ha": 20000},
    "mothbeans":    {"yield_per_ha": 0.8,  "price_per_ton": 50000, "invest_per_ha": 18000},
    "mungbean":     {"yield_per_ha": 0.9,  "price_per_ton": 52000, "invest_per_ha": 19000},
    "blackgram":    {"yield_per_ha": 0.9,  "price_per_ton": 55000, "invest_per_ha": 20000},
    "lentil":       {"yield_per_ha": 1.0,  "price_per_ton": 60000, "invest_per_ha": 22000},
    "pomegranate":  {"yield_per_ha": 8.0,  "price_per_ton": 80000, "invest_per_ha": 120000},
    "banana":       {"yield_per_ha": 30.0, "price_per_ton": 12000, "invest_per_ha": 80000},
    "mango":        {"yield_per_ha": 8.0,  "price_per_ton": 35000, "invest_per_ha": 60000},
    "grapes":       {"yield_per_ha": 12.0, "price_per_ton": 45000, "invest_per_ha": 150000},
    "watermelon":   {"yield_per_ha": 25.0, "price_per_ton": 8000,  "invest_per_ha": 60000},
    "muskmelon":    {"yield_per_ha": 15.0, "price_per_ton": 10000, "invest_per_ha": 55000},
    "apple":        {"yield_per_ha": 10.0, "price_per_ton": 70000, "invest_per_ha": 200000},
    "orange":       {"yield_per_ha": 10.0, "price_per_ton": 25000, "invest_per_ha": 70000},
    "papaya":       {"yield_per_ha": 40.0, "price_per_ton": 7000,  "invest_per_ha": 50000},
    "coconut":      {"yield_per_ha": 14.0, "price_per_ton": 22000, "invest_per_ha": 40000},
    "cotton":       {"yield_per_ha": 1.8,  "price_per_ton": 60000, "invest_per_ha": 45000},
    "jute":         {"yield_per_ha": 2.5,  "price_per_ton": 35000, "invest_per_ha": 30000},
    "coffee":       {"yield_per_ha": 1.0,  "price_per_ton": 200000,"invest_per_ha": 80000},
}

# Default profile for crops not in our database
DEFAULT_PROFILE = {"yield_per_ha": 2.0, "price_per_ton": 30000, "invest_per_ha": 30000}


def calculate_economics(crop: str, farm_area_hectares: float) -> dict:
    """
    Calculates financial economics for growing a specific crop on a given farm area.

    Parameters
    ----------
    crop                 : str   — crop name (lowercase, must be in CROP_PROFILES)
    farm_area_hectares   : float — farm area in hectares

    Returns
    -------
    dict with keys:
        - success               : bool
        - crop                  : str
        - farm_area_ha          : float
        - total_yield_tons      : float
        - total_investment_inr  : float
        - total_revenue_inr     : float
        - net_profit_inr        : float
        - profit_margin_pct     : float
        - roi_pct               : float  (return on investment)
        - yield_per_ha          : float
        - price_per_ton_inr     : float
        - invest_per_ha_inr     : float
        - error                 : str (only on failure)
    """
    try:
        profile = CROP_PROFILES.get(crop.lower(), DEFAULT_PROFILE)

        y_per_ha   = profile["yield_per_ha"]
        price      = profile["price_per_ton"]
        invest_ha  = profile["invest_per_ha"]

        total_yield  = round(y_per_ha * farm_area_hectares, 2)
        total_invest = round(invest_ha * farm_area_hectares, 2)
        total_revenue= round(total_yield * price, 2)
        net_profit   = round(total_revenue - total_invest, 2)
        margin       = round((net_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0.0
        roi          = round((net_profit / total_invest) * 100, 1) if total_invest > 0 else 0.0

        return {
            "success":               True,
            "crop":                  crop.lower(),
            "farm_area_ha":          farm_area_hectares,
            "total_yield_tons":      total_yield,
            "total_investment_inr":  total_invest,
            "total_revenue_inr":     total_revenue,
            "net_profit_inr":        net_profit,
            "profit_margin_pct":     margin,
            "roi_pct":               roi,
            "yield_per_ha":          y_per_ha,
            "price_per_ton_inr":     price,
            "invest_per_ha_inr":     invest_ha,
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = calculate_economics("rice", 2.5)
    print("[Economics Test]")
    for k, v in result.items():
        print(f"  {k}: {v}")
