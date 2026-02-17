import numpy as np


def get_historical_anchor(similar_campaigns):
    """
    Robust median delivered CPM from similar campaigns.
    Requires >= 3 valid CPMs to activate.
    """
    if not isinstance(similar_campaigns, list):
        return None

    cpms = []
    for c in similar_campaigns:
        try:
            val = c.get("delivered_cpm")
            if val is not None and not np.isnan(val):
                cpms.append(float(val))
        except Exception:
            continue

    if len(cpms) >= 3:
        return float(np.median(cpms))

    return None


def blend_ml_and_history(ml_cpm, hist_cpm, hist_weight=0.35):
    """
    Blend ML prediction with historical CPM anchor.
    hist_weight ∈ [0.2, 0.5]
    """
    if hist_cpm is None:
        return float(ml_cpm)

    return (
        (1 - hist_weight) * float(ml_cpm)
        + hist_weight * float(hist_cpm)
    )


def apply_llm_adjustment(base_cpm, adjustment_factor):
    """
    LLM is a bounded nudge, not a driver.
    """
    if adjustment_factor is None:
        adjustment_factor = 1.0

    adjustment_factor = float(
        max(0.90, min(1.15, adjustment_factor))
    )

    return base_cpm * adjustment_factor


def compute_final_cpm(
    pred,
    similar_campaigns,
    llm_adjustment_factor,
    hist_weight=0.35
):
    model_range = pred["model_range"]
    conformal_range = pred["conformal_range"]
    llm_range = pred["llm_adjusted_range"]

    ml_cpm = float(model_range["p90"])

    hist_cpm = get_historical_anchor(similar_campaigns)

    blended_cpm = blend_ml_and_history(
        ml_cpm=ml_cpm,
        hist_cpm=hist_cpm,
        hist_weight=hist_weight
    )

    adjusted_cpm = apply_llm_adjustment(
        blended_cpm,
        llm_adjustment_factor
    )

    conformal_high = float(conformal_range["high"])
    llm_high = float(llm_range["llm_predicted_cpm"]["high"])

    final_cpm = max(conformal_high, adjusted_cpm)
    final_cpm = min(final_cpm, llm_high)

    return round(final_cpm, 2)

