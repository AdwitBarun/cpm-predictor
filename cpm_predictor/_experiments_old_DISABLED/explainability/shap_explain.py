import shap

def explain_instance(model, X_row):
    explainer = shap.TreeExplainer(model)
    return explainer.shap_values(X_row)
