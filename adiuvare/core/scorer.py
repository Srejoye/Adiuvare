from ..core.models import SignalResult

_weights = {
    "payload": 0.40,
    "behavior": 0.35,
    "identity": 0.25,
    "context": 0.10,
    "ip_rep": 0.05,
}


def compute_score(sig_res: dict[str, SignalResult], snap=None) -> tuple[float, dict[str, float]]:
    breakdown: dict[str, float] = {}
    total = 0.0
    active = 0

    weights = dict(_weights)
    if snap:
        weights["payload"] = snap.payload_weight
        weights["behavior"] = snap.behavior_weight
        weights["identity"] = snap.identity_weight
        # When snap overrides the 3 main weights (summing to 1.0), context and
        # ip_rep from _weights (0.10 + 0.05 = 0.15) are still added on top,
        # inflating the total to 1.15. Normalize to keep the sum at 1.0.
        # (issue #135: false positive blocks from weight arithmetic)
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

    for name, res in sig_res.items():
        weight = weights.get(name, 0.0)
        part = res.score * weight
        breakdown[name] = part
        total += part
        if res.score > 0.0:
            active += 1

    if active > 1:
        total += 0.01

    return min(total, 1.0), breakdown
