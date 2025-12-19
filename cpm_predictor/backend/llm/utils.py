def decode_tg(tg: str) -> str:
    if not tg:
        return "Unknown audience"

    tg = tg.upper()

    gender = "Mixed"
    if tg.startswith("F"):
        gender = "Female"
    elif tg.startswith("M"):
        gender = "Male"

    age_part = tg[1:] if tg[0] in {"F", "M"} else tg
    return f"{gender}, age {age_part}"


def get_tg_premium_factor(tg: str) -> str:
    if not tg:
        return "Standard CPM potential"

    if "15-44" in tg or "25-44" in tg:
        return "High CPM potential (prime working-age audience)"
    if "18-24" in tg:
        return "Moderate CPM potential (youth audience)"
    return "Standard CPM potential"


def get_seasonal_factors(month_range: str, current_month: str) -> str:
    festive_months = {"October", "November", "December"}

    if current_month in festive_months:
        return "Festive season – increased advertiser demand"

    return "Normal demand period"
