import os

THRESHOLD = float(os.environ.get("THRESHOLD", 0.5))
# VARIANCE_THRESHOLD = float(os.environ.get("VARIANCE_THRESHOLD", "0.01"))
# FLIP_THRESHOLD = float(os.environ.get("FLIP_THRESHOLD", "0.05"))
MISSING_RATE_THRESHOLD = float(os.environ.get("MISSING_RATE_THRESHOLD", 0.3))
def decision(request_id: str, score: float, missing_rate: float):
    prediction = int(score >= THRESHOLD)
    print("missing rate: ", missing_rate)
    if missing_rate > MISSING_RATE_THRESHOLD:
        abstained = True
        reason = "instability"
    else:
        abstained = False
        reason = None
    return {
        "request_id": request_id,
        "score": score,
        "prediction": prediction,
        "abstained": abstained,
        "reason": reason
    }
