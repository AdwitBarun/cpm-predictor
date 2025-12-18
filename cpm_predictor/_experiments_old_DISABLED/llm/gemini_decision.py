import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_decision(pred_range, shap_features, client_cpm):
    prompt = f"""
You are an ad-tech expert.

Predicted CPM range:
P10: {pred_range[0]:.2f}
P50: {pred_range[1]:.2f}
P90: {pred_range[2]:.2f}

Client CPM: {client_cpm}

Top drivers:
{shap_features}

Classify feasibility as SAFE, CHALLENGING, or NOT FEASIBLE.
Explain why and suggest changes.
"""
    model = genai.GenerativeModel("gemini-pro")
    return model.generate_content(prompt).text
