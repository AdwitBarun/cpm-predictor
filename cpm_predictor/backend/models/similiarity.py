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

    Parameters
    ----------
    X_new : pd.DataFrame
        Single-row engineered feature dataframe
    X_hist : pd.DataFrame
        Engineered features of historical campaigns
    meta_df : pd.DataFrame
        Metadata for historical campaigns (same index as X_hist)
    k : int
        Number of similar campaigns to return
    min_similarity : float
        Threshold to avoid junk matches
    verbose : bool
        Print diagnostics

    Returns
    -------
    List[dict]
        UI-ready list of similar campaigns
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
    X_new_vec = X_new.values

    # -----------------------------
    # Cosine similarity
    # -----------------------------
    similarities = cosine_similarity(X_new_vec, X_hist.values)[0]

    sim_df = meta_df.copy()
    sim_df["similarity_score"] = similarities

    # Filter weak matches
    sim_df = sim_df[sim_df["similarity_score"] >= min_similarity]

    # Sort & select top-k
    sim_df = sim_df.sort_values(
        "similarity_score", ascending=False
    ).head(k)

    if verbose:
        print("\nTop similar campaigns:")
        print(sim_df[["campaign_name", "similarity_score", "delivered_cpm"]])

    # -----------------------------
    # Build UI-friendly response
    # -----------------------------
    results = []

    for _, row in sim_df.iterrows():
        results.append({
            "campaign_id": row.get("campaign_id"),
            "campaign_name": row.get("campaign_name"),
            "similarity_score": round(row["similarity_score"], 3),

            "delivered_cpm": round(row.get("delivered_cpm", np.nan), 2),

            "markets": row.get("markets"),
            "device_summary": row.get("device_summary"),
            "tg_summary": row.get("tg_summary"),

            "start_month": row.get("start_month"),
            "campaign_intensity": round(
                row.get("campaign_intensity", np.nan), 2
            )
        })

    return results
