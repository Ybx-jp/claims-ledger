def classify_risk(score: float) -> str:
    if score >= 0.72:
        return "review"
    return "normal"


def serialize_risk(claim_id: str, score: float) -> dict[str, object]:
    return {"claim_id": claim_id, "score": score, "decision": classify_risk(score)}
