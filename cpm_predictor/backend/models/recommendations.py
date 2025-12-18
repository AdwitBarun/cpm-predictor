def suggest_actions(shap_features):
    actions = []
    for feat, val in shap_features:
        if "Frequency" in feat and val > 0:
            actions.append("Reduce frequency cap")
        if "Pacing" in feat and val > 0:
            actions.append("Relax pacing constraints")
        if "Inventory Mode" in feat and val > 0:
            actions.append("Broaden inventory access")
    return list(set(actions))
