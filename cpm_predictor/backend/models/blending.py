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


# def compute_final_cpm(
#     pred,
#     similar_campaigns,
#     llm_result,
#     hist_weight=0.35
# ):
#     model_range = pred["model_range"]
#     conformal_range = pred["conformal_range"]

#     ml_cpm = float(model_range["p90"])

#     hist_cpm = get_historical_anchor(similar_campaigns)

#     blended_cpm = blend_ml_and_history(
#         ml_cpm=ml_cpm,
#         hist_cpm=hist_cpm,
#         hist_weight=hist_weight
#     )

#     adjusted_cpm = apply_llm_adjustment(
#         blended_cpm,
#         llm_result["adjustment_factor"]
#     )

#     conformal_high = float(conformal_range["high"])
#     llm_high = float(llm_result["llm_predicted_cpm"]["high"])

#     final_cpm = max(conformal_high, adjusted_cpm)
#     final_cpm = min(final_cpm, llm_high)

#     return round(final_cpm, 2)

import numpy as np

def compute_final_cpm(
    pred,
    similar_campaigns,
    llm_result,
    hist_weight=0.35
):
    model_range = pred["model_range"]
    conformal_range = pred["conformal_range"]

    # -----------------------------
    # 1️⃣ ML Risk-Aware Estimate
    # -----------------------------
    ml_mid = float(model_range["p50"])
    ml_p90 = float(model_range["p90"])
    ml_spread = max(0, ml_p90 - ml_mid)

    # More stable than raw p90
    ml_cpm = ml_mid + 0.6 * ml_spread


    # -----------------------------
    # 2️⃣ Historical Anchor
    # -----------------------------
    hist_cpms = [
        float(c["delivered_cpm"])
        for c in similar_campaigns
        if c.get("delivered_cpm") is not None
    ]

    hist_cpm = None
    hist_std = None

    if len(hist_cpms) >= 2:
        hist_cpm = float(np.median(hist_cpms))
        hist_std = float(np.std(hist_cpms))
    elif len(hist_cpms) == 1:
        hist_cpm = hist_cpms[0]
        hist_std = 0


    # Reliability weight grows with volume
    n = len(hist_cpms)
    dynamic_hist_weight = min(0.7, hist_weight * (n / (n + 2)))

    if hist_cpm:
        blended_cpm = (
            (1 - dynamic_hist_weight) * ml_cpm +
            dynamic_hist_weight * hist_cpm
        )
    else:
        blended_cpm = ml_cpm


    # -----------------------------
    # 3️⃣ Downside Protection Rule
    # -----------------------------
    # If history strongly contradicts ML, prevent underpricing
    if hist_cpm:
        if hist_cpm > ml_cpm * 1.12:
            blended_cpm = max(blended_cpm, 0.9 * hist_cpm)


    # -----------------------------
    # 4️⃣ LLM Adjustment (Soft Clamp)
    # -----------------------------
    adj_factor = llm_result["adjustment_factor"]
    adj_factor = max(0.9, min(adj_factor, 1.1))

    adjusted_cpm = blended_cpm * adj_factor


    # -----------------------------
    # 5️⃣ Smooth Upper Anchoring
    # -----------------------------
    conformal_high = float(conformal_range["high"])
    llm_high = float(llm_result["llm_predicted_cpm"]["high"])

    upper_anchor = 0.65 * conformal_high + 0.35 * llm_high

    # Instead of hard min, apply soft cap
    final_cpm = min(adjusted_cpm, upper_anchor)

    return round(final_cpm, 2)

