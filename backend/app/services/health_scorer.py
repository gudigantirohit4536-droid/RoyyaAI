from dataclasses import dataclass


@dataclass
class HealthScore:
    score: float          # 0-100
    status: str           # critical / warning / good / excellent
    breakdown: dict       # per-parameter scores
    alerts: list[str]     # specific warnings


def _score_param(value: float, optimal_min: float, optimal_max: float,
                 warn_min: float, warn_max: float) -> float:
    """Returns 0-100 score for a single parameter."""
    if optimal_min <= value <= optimal_max:
        return 100.0
    if warn_min <= value < optimal_min:
        return 100.0 * (value - warn_min) / (optimal_min - warn_min)
    if optimal_max < value <= warn_max:
        return 100.0 * (warn_max - value) / (warn_max - optimal_max)
    return 0.0


def calculate_health_score(
    dissolved_oxygen: float | None = None,
    ph: float | None = None,
    salinity: float | None = None,
    temperature: float | None = None,
    alkalinity: float | None = None,
    ammonia: float | None = None,
    nitrite: float | None = None,
    secchi_depth: float | None = None,
) -> HealthScore:

    # (weight, score, alert_message_if_zero)
    weights = {
        "dissolved_oxygen": 30,
        "ph": 20,
        "temperature": 15,
        "ammonia": 15,
        "nitrite": 10,
        "salinity": 5,
        "alkalinity": 3,
        "secchi_depth": 2,
    }

    scores: dict[str, float] = {}
    alerts: list[str] = []

    if dissolved_oxygen is not None:
        s = _score_param(dissolved_oxygen, 5.0, 8.0, 3.0, 12.0)
        scores["dissolved_oxygen"] = s
        if dissolved_oxygen < 3.0:
            alerts.append(f"URGENT: DO critically low at {dissolved_oxygen} mg/L — turn on all aerators immediately")
        elif dissolved_oxygen < 4.0:
            alerts.append(f"WARNING: DO low at {dissolved_oxygen} mg/L — increase aeration")

    if ph is not None:
        s = _score_param(ph, 7.5, 8.5, 7.0, 9.5)
        scores["ph"] = s
        if ph < 7.0:
            alerts.append(f"WARNING: pH too low at {ph} — add agricultural lime")
        elif ph > 9.0:
            alerts.append(f"WARNING: pH too high at {ph} — partial water exchange needed")

    if temperature is not None:
        s = _score_param(temperature, 25.0, 30.0, 20.0, 35.0)
        scores["temperature"] = s
        if temperature < 22.0:
            alerts.append(f"WARNING: Temperature low at {temperature}°C — White Spot Disease risk increases")
        elif temperature > 33.0:
            alerts.append(f"WARNING: Temperature high at {temperature}°C — DO will drop, increase aeration")

    if ammonia is not None:
        s = _score_param(ammonia, 0.0, 0.5, 0.0, 2.0)
        scores["ammonia"] = s
        if ammonia > 1.0:
            alerts.append(f"URGENT: Ammonia toxic at {ammonia} mg/L — stop feeding, add probiotics")
        elif ammonia > 0.5:
            alerts.append(f"WARNING: Ammonia elevated at {ammonia} mg/L — reduce feeding 30%")

    if nitrite is not None:
        s = _score_param(nitrite, 0.0, 0.1, 0.0, 1.0)
        scores["nitrite"] = s
        if nitrite > 0.5:
            alerts.append(f"URGENT: Nitrite toxic at {nitrite} mg/L — add salt 50kg/acre, water exchange")
        elif nitrite > 0.1:
            alerts.append(f"WARNING: Nitrite elevated at {nitrite} mg/L — add probiotics")

    if salinity is not None:
        s = _score_param(salinity, 10.0, 25.0, 2.0, 40.0)
        scores["salinity"] = s
        if salinity < 2.0:
            alerts.append(f"WARNING: Salinity very low at {salinity} ppt — monitor for stress")
        elif salinity > 35.0:
            alerts.append(f"WARNING: Salinity very high at {salinity} ppt — dilute with fresh water")

    if alkalinity is not None:
        s = _score_param(alkalinity, 80.0, 150.0, 40.0, 200.0)
        scores["alkalinity"] = s
        if alkalinity < 60.0:
            alerts.append(f"WARNING: Alkalinity low at {alkalinity} mg/L — add lime 10-20 kg/acre")

    if secchi_depth is not None:
        s = _score_param(secchi_depth, 25.0, 45.0, 15.0, 70.0)
        scores["secchi_depth"] = s
        if secchi_depth < 20.0:
            alerts.append(f"WARNING: Water too turbid (secchi {secchi_depth}cm) — algae bloom risk")
        elif secchi_depth > 60.0:
            alerts.append(f"WARNING: Water too clear (secchi {secchi_depth}cm) — phytoplankton too low")

    if not scores:
        return HealthScore(score=0.0, status="unknown", breakdown={}, alerts=["No water quality data entered"])

    total_weight = sum(weights[k] for k in scores)
    weighted_sum = sum(scores[k] * weights[k] for k in scores)
    final_score = round(weighted_sum / total_weight, 1)

    if final_score >= 85:
        status = "excellent"
    elif final_score >= 65:
        status = "good"
    elif final_score >= 40:
        status = "warning"
    else:
        status = "critical"

    return HealthScore(
        score=final_score,
        status=status,
        breakdown={k: round(v, 1) for k, v in scores.items()},
        alerts=alerts,
    )
