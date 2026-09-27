"""Trust-weighted, time-decayed resolution for real-time safety reports."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SafetyReport

TRUST_WEIGHTS = {"police": 1.0, "rescue_team": 1.0, "news": 0.8, "user": 0.15}
HALF_LIFE_MINUTES = 45.0
OFFICIAL_FLOOR = 0.3
# The original trust-weighted model is retained: user weight must sum to 1.0
# before it independently flags a target unsafe.
USER_CORROBORATION_THRESHOLD = 1.0
# The additive threshold alone requires seven fresh user reports (7 × 0.15),
# which conflicts with the required four-report corroboration behaviour. A
# second, explicit corroboration rule resolves that contradiction below.
USER_MIN_INDEPENDENT_REPORTERS = 4
USER_WINDOW = timedelta(hours=2)
USER_RADIUS_METERS = 500.0


@dataclass(frozen=True)
class ResolvedSafetyStatus:
    status: str  # safe | unsafe | unconfirmed
    confidence: float
    contributing_report_count: int


@dataclass(frozen=True)
class RiskMeter:
    score: float
    band: str
    report_count: int
    last_report_at: datetime | None


def risk_meter_band(score: float) -> str:
    """Classify the documented, inclusive-lower-bound risk-meter bands."""
    return "low" if score < 25 else "rising" if score < 50 else "elevated" if score < 75 else "critical"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def decayed_weight(report: SafetyReport, now: datetime | None = None) -> float:
    now = now or _now()
    if getattr(report, "verification_decision", None) == "dismiss":
        return 0.0
    created = report.created_at if report.created_at.tzinfo else report.created_at.replace(tzinfo=timezone.utc)
    age_minutes = max(0.0, (now - created).total_seconds() / 60)
    # A responder-confirmed report is trusted evidence, irrespective of its
    # original source. Production authorization belongs at the API boundary.
    trust = 1.0 if getattr(report, "verification_decision", None) == "confirm" else TRUST_WEIGHTS[report.source_type]
    return trust * 0.5 ** (age_minutes / HALF_LIFE_MINUTES)


def _distance_meters(first_lat: float, first_lng: float, second_lat: float, second_lng: float) -> float:
    lat1, lng1, lat2, lng2 = map(radians, (first_lat, first_lng, second_lat, second_lng))
    value = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lng2 - lng1) / 2) ** 2
    return 6_371_008.8 * 2 * asin(sqrt(value))


def _reporter_key(report: SafetyReport, fallback_index: int) -> str:
    """Prefer a device/session identity; use report ID for anonymous reports.

    A report ID is unique in the database. ``fallback_index`` makes unit-test
    fixtures without persisted IDs deterministic while never merging objects.
    """
    if getattr(report, "reporter_id", None):
        return f"reporter:{report.reporter_id}"
    if getattr(report, "id", None) is not None:
        return f"report:{report.id}"
    return f"fixture:{fallback_index}"


def _independent_reports(reports: list[SafetyReport], now: datetime) -> list[SafetyReport]:
    """Keep only the strongest current report for each reporter identity."""
    strongest: dict[str, SafetyReport] = {}
    for index, report in enumerate(reports):
        key = _reporter_key(report, index)
        if key not in strongest or decayed_weight(report, now) > decayed_weight(strongest[key], now):
            strongest[key] = report
    return list(strongest.values())


def _created_at(report: SafetyReport) -> datetime:
    return report.created_at if report.created_at.tzinfo else report.created_at.replace(tzinfo=timezone.utc)


def _is_active_user_report(report: SafetyReport, now: datetime) -> bool:
    return (
        report.source_type == "user"
        and report.status in {"unsafe", "blocked"}
        and getattr(report, "verification_decision", None) != "dismiss"
        and now - _created_at(report) <= USER_WINDOW
    )


def _user_contributors(reports: list[SafetyReport], *, latitude: float | None, longitude: float | None, now: datetime) -> tuple[list[SafetyReport], list[SafetyReport]]:
    """Return active local reports and their independent 500 m contributors."""
    user_reports = [report for report in reports if _is_active_user_report(report, now)]
    if latitude is not None and longitude is not None:
        local = [report for report in user_reports if report.latitude is not None and report.longitude is not None and _distance_meters(latitude, longitude, report.latitude, report.longitude) <= USER_RADIUS_METERS]
        return local, _independent_reports(local, now)
    candidates = [report for report in user_reports if report.latitude is not None and report.longitude is not None]
    clusters = [[other for other in candidates if _distance_meters(report.latitude, report.longitude, other.latitude, other.longitude) <= USER_RADIUS_METERS] for report in candidates]
    local = max(clusters, key=lambda cluster: sum(decayed_weight(item, now) for item in cluster), default=[])
    return local, _independent_reports(local, now)


def resolve_reports(reports: Iterable[SafetyReport], *, latitude: float | None = None, longitude: float | None = None, now: datetime | None = None) -> ResolvedSafetyStatus:
    """Resolve supplied reports without mutating them or trusting stale input."""
    now = now or _now()
    current = list(reports)
    official = [
        report for report in current
        if (report.source_type != "user" or getattr(report, "verification_decision", None) == "confirm")
        and report.status in {"unsafe", "blocked"}
        and decayed_weight(report, now) > OFFICIAL_FLOOR
    ]
    if official:
        return ResolvedSafetyStatus("unsafe", round(max(decayed_weight(report, now) for report in official), 3), len(official))
    # Only danger reports participate. Current schema has no "dismissed"
    # status; safe/clear (and any future dismissed value) are excluded here.
    # Target-linked user reports still need geographic corroboration; choose
    # the strongest 500 m cluster rather than combining distant reports.
    user_reports, contributors = _user_contributors(current, latitude=latitude, longitude=longitude, now=now)
    weighted = sum(decayed_weight(report, now) for report in contributors)
    # Deterministic user corroboration rule: each distinct reporter contributes
    # one freshness unit at creation, decaying by the same 45-minute curve as
    # its trust weight. Four fresh identities therefore give four units; repeat
    # posts from one reporter never add units. This sits alongside—not instead
    # of—the original 1.0 trust-weight threshold.
    corroboration_units = sum(decayed_weight(report, now) / TRUST_WEIGHTS["user"] for report in contributors)
    if weighted >= USER_CORROBORATION_THRESHOLD or corroboration_units >= USER_MIN_INDEPENDENT_REPORTERS:
        return ResolvedSafetyStatus("unsafe", round(min(1.0, weighted), 3), len(contributors))
    if user_reports:
        return ResolvedSafetyStatus("unconfirmed", round(weighted, 3), len(contributors))
    return ResolvedSafetyStatus("safe", 1.0, 0)


def get_risk_meter(session: Session, target_type: str, target_id: int, *, now: datetime | None = None) -> RiskMeter:
    """Return a 0-100 view of the active evidence used by ``resolve_target``.

    Score is ``100 * min(1, active_weight)``. Active weight is the summed
    decayed trust of the same independently reported 500 m user cluster and
    active official/confirmed evidence used by status resolution. If that
    evidence resolves the target as unsafe (including the explicit four-user
    corroboration rule), the score has a 75-point floor: an unsafe target is
    always in the ``critical`` band. Dismissed, stale, safe, and clear reports
    contribute zero. This makes the meter a normalized presentation of the
    resolver rather than a second risk model.
    """
    now = now or _now()
    reports = reports_for_target(session, target_type, target_id)
    official = [
        report for report in reports
        if (report.source_type != "user" or getattr(report, "verification_decision", None) == "confirm")
        and report.status in {"unsafe", "blocked"}
        and decayed_weight(report, now) > OFFICIAL_FLOOR
    ]
    _, users = _user_contributors(reports, latitude=None, longitude=None, now=now)
    evidence = official + [report for report in users if report not in official]
    weighted = sum(decayed_weight(report, now) for report in evidence)
    resolved = resolve_reports(reports, now=now)
    score = min(100.0, weighted * 100)
    if resolved.status == "unsafe":
        score = max(score, 75.0)
    score = round(score, 2)
    band = risk_meter_band(score)
    last_report_at = max((_created_at(report) for report in evidence), default=None)
    return RiskMeter(score=score, band=band, report_count=len(evidence), last_report_at=last_report_at)


def reports_for_target(session: Session, target_type: str, target_id: int | None) -> list[SafetyReport]:
    return list(session.scalars(select(SafetyReport).where(SafetyReport.target_type == target_type, SafetyReport.target_id == target_id)))


def resolve_target(session: Session, target_type: str, target_id: int, *, latitude: float | None = None, longitude: float | None = None) -> ResolvedSafetyStatus:
    return resolve_reports(reports_for_target(session, target_type, target_id), latitude=latitude, longitude=longitude)


def unsafe_target_ids(session: Session, target_type: str) -> set[int]:
    """Resolve candidates once per graph/ranking build; report target IDs only."""
    ids = set(session.scalars(select(SafetyReport.target_id).where(SafetyReport.target_type == target_type, SafetyReport.target_id.is_not(None))))
    return {target_id for target_id in ids if resolve_target(session, target_type, target_id).status == "unsafe"}
