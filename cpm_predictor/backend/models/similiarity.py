# models/similarity.py

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def find_similar_campaigns(
    X_new: pd.DataFrame,
    X_hist: pd.DataFrame,
    meta_df: pd.DataFrame,
    k: int = 5,
    min_similarity: float = 0.2,
    verbose: bool = False
):
    """
    Find top-k most similar historical campaigns.
    """

    # -----------------------------
    # Safety checks
    # -----------------------------
    assert len(X_new) == 1, "X_new must contain exactly one row"
    assert X_hist.index.equals(meta_df.index), "X_hist and meta_df must align"

    # -----------------------------
    # Align feature space
    # -----------------------------
    X_hist = X_hist.reindex(columns=X_new.columns, fill_value=0)

    # -----------------------------
    # 🔥 CRITICAL FIX: cosine similarity cannot handle NaN
    # -----------------------------
    X_new_clean = X_new.fillna(0)
    X_hist_clean = X_hist.fillna(0)

    # -----------------------------
    # Cosine similarity
    # -----------------------------
    similarities = cosine_similarity(
        X_new_clean.values,
        X_hist_clean.values
    )[0]
    min_len = min(len(meta_df), len(similarities))

    sim_df = meta_df.iloc[:min_len].copy()
    sim_df["similarity_score"] = similarities[:min_len]

    # Filter weak matches
    sim_df = sim_df[sim_df["similarity_score"] >= min_similarity]

    # Sort & select top-k
    sim_df = sim_df.sort_values(
        "similarity_score", ascending=False
    ).head(k)

    if verbose and not sim_df.empty:
        print("\nTop similar campaigns:")
        print(sim_df[["campaign_name", "similarity_score", "delivered_cpm"]])

    # -----------------------------
    # Build UI-friendly response
    # -----------------------------
    results = []

    for _, row in sim_df.iterrows():

        delivered = pd.to_numeric(
            row.get("delivered_cpm", np.nan),
            errors="coerce"
        )

        intensity = pd.to_numeric(
            row.get("campaign_intensity", np.nan),
            errors="coerce"
        )

        results.append({
            "campaign_id": row.get("campaign_id"),
            "campaign_name": row.get("campaign_name"),
            "similarity_score": round(float(row["similarity_score"]), 3),

            "delivered_cpm": (
                round(float(delivered), 2)
                if not pd.isna(delivered) else None
            ),

            "markets": row.get("markets"),
            "device_summary": row.get("device_summary"),
            "tg_summary": row.get("tg_summary"),

            "start_month": row.get("start_month"),

            "campaign_intensity": (
                round(float(intensity), 2)
                if not pd.isna(intensity) else None
            ),
        })

    return results
