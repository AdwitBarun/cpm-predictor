import numpy as np

def confidence_score(p10, p50, p90):
    width = p90 - p10
    if width <= 0:
        return 0.2
    return round(float(np.exp(-width / p50)), 2)
