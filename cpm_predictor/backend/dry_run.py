"""
Dry run script to test full CPM prediction pipeline:
- ML quantile models
- SHAP explanations
- Gemini LLM adjustment
- Final blended CPM range
"""

import joblib
import pandas as pd

from cpm_predictor.backend.features.preprocess import preprocess
from cpm_predictor.backend.models.shap_explainer import explain_prediction
from cpm_predictor.backend.llm.gemini_client import gemini_range


# -------------------------------------------------
# Load artifacts (✅ correct filenames)
# -------------------------------------------------
ARTIFACT_DIR = "cpm_predictor/backend/artifacts"

MODELS = joblib.load(f"{ARTIFACT_DIR}/cpm_quantile_models.pkl")
FEATURE_COLUMNS = joblib.load(f"{ARTIFACT_DIR}/feature_columns.pkl")


# -------------------------------------------------
# Sample input (EDIT THIS FREELY)
# -------------------------------------------------
INPUT_DATA = {
    "Device": "YT NSk",
    "TG": "F25-44",
    "Geography_Targeting_Include": "1007785;9040240",
    "Planned_Budget": 400000,
    "Planned_Impressions": 2000000,
    "Planned_Freq": 6,
    "Inventory_Mode": "Limited",
    "Video_Ad_Format": "Non Skippable",
    "TrueView_Video_Ad_Formats": "Skippable / Bumper / Non Skippable",
    "month_range": "Jul–Sep 2025",
    "campaign_duration_days": 60,
}


# -------------------------------------------------
# Helper: robust quantile fetch
# -------------------------------------------------
def get_model(models, q):
    """
    Supports float or string quantile keys.
    """
    if q in models:
        return models[q]
    if str(q) in models:
        return models[str(q)]
    raise KeyError(f"Quantile {q} not found. Available keys: {models.keys()}")


def main():
    print("\n==============================")
    print("🚀 CPM PREDICTION DRY RUN")
    print("==============================\n")

    # -------------------------------------------------
    # 1️⃣ Preprocess
    # -------------------------------------------------
    X = preprocess(INPUT_DATA, FEATURE_COLUMNS)

    print("Input after preprocessing:")
    print(X.head(), "\n")
    print("Loaded model keys:", MODELS.keys(), "\n")

    # -------------------------------------------------
    # 2️⃣ Historical quantile predictions (✅ FIXED)
    # -------------------------------------------------
    p10 = float(get_model(MODELS, 0.1).predict(X)[0])
    p50 = float(get_model(MODELS, 0.5).predict(X)[0])
    p90 = float(get_model(MODELS, 0.9).predict(X)[0])

    print("📊 Historical CPM range:")
    print(f"  P10: {p10:.2f}")
    print(f"  P50: {p50:.2f}")
    print(f"  P90: {p90:.2f}\n")

    # -------------------------------------------------
    # 3️⃣ SHAP explanation (median model)
    # -------------------------------------------------
    shap_summary = explain_prediction(get_model(MODELS, 0.5), X)

    print("🧠 Top SHAP features:")
    for feat, val in shap_summary:
        print(f"  {feat}: {val:.4f}")
    print()

    # -------------------------------------------------
    # 4️⃣ Gemini LLM adjustment
    # -------------------------------------------------
    llm_result = gemini_range(
        features=INPUT_DATA,
        historical_range=(p10, p50, p90),
        shap_summary=shap_summary,
    )

    print("🤖 Gemini-adjusted CPM range:")
    print(llm_result, "\n")

    # -------------------------------------------------
    # 5️⃣ Final blended range
    # -------------------------------------------------
    final_low = 0.65 * p10 + 0.35 * llm_result["low"]
    final_high = 0.65 * p90 + 0.35 * llm_result["high"]

    print("✅ FINAL CPM RANGE:")
    print(f"  Low : {final_low:.2f}")
    print(f"  High: {final_high:.2f}\n")

    print("📝 Explanation:")
    print(llm_result["explanation"])

    print("\n==============================")
    print("✅ DRY RUN COMPLETE")
    print("==============================\n")


if __name__ == "__main__":
    main()
