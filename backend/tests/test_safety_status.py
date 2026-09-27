from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.safety_status import HALF_LIFE_MINUTES, decayed_weight, get_risk_meter, resolve_reports, risk_meter_band


NOW = datetime(2026, 9, 27, 12, 0, tzinfo=timezone.utc)


def report(
    source: str,
    *,
    reporter_id: str | None = None,
    status: str = "unsafe",
    latitude: float = 12.9,
    longitude: float = 77.5,
    created_at: datetime = NOW,
):
    return SimpleNamespace(
        source_type=source,
        status=status,
        reporter_id=reporter_id,
        latitude=latitude,
        longitude=longitude,
        created_at=created_at,
    )


def test_zero_reports_are_safe():
    assert resolve_reports([], latitude=12.9, longitude=77.5, now=NOW).status == "safe"


def test_single_user_report_is_unconfirmed_not_unsafe():
    result = resolve_reports([report("user")], latitude=12.9, longitude=77.5, now=NOW)
    assert result.status == "unconfirmed"


def test_single_official_report_is_unsafe():
    result = resolve_reports([report("police")], latitude=12.9, longitude=77.5, now=NOW)
    assert result.status == "unsafe"


def test_four_fresh_user_reports_are_corroborated_unsafe():
    result = resolve_reports([report("user", reporter_id=f"device-{index}") for index in range(4)], latitude=12.9, longitude=77.5, now=NOW)
    assert result.status == "unsafe"
    assert result.contributing_report_count == 4


def test_duplicate_reports_from_one_user_do_not_manufacture_corroboration():
    result = resolve_reports([report("user", reporter_id="same-device") for _ in range(4)], latitude=12.9, longitude=77.5, now=NOW)
    assert result.status == "unconfirmed"
    assert result.contributing_report_count == 1


def test_reports_outside_500_meters_do_not_corroborate():
    # About 1.1 km north of the target, so it cannot join the local cluster.
    reports = [report("user", reporter_id=f"device-{index}", latitude=12.91) for index in range(4)]
    assert resolve_reports(reports, latitude=12.9, longitude=77.5, now=NOW).status == "safe"


def test_reports_older_than_two_hours_do_not_corroborate():
    stale = NOW.replace(hour=9, minute=59)
    reports = [report("user", reporter_id=f"device-{index}", created_at=stale) for index in range(4)]
    assert resolve_reports(reports, latitude=12.9, longitude=77.5, now=NOW).status == "safe"


def test_decay_halves_a_user_report_after_45_minutes():
    created_at = NOW.replace(hour=11, minute=15)
    assert decayed_weight(report("user", created_at=created_at), now=NOW) == 0.15 * 0.5
    assert HALF_LIFE_MINUTES == 45.0


def test_safe_and_clear_reports_do_not_create_unsafe_status():
    reports = [
        report("user", reporter_id="safe-user", status="safe"),
        report("police", status="clear"),
    ]
    assert resolve_reports(reports, latitude=12.9, longitude=77.5, now=NOW).status == "safe"


class ReportSession:
    def __init__(self, reports):
        self.reports = reports

    def scalars(self, _statement):
        return self.reports


def test_risk_meter_zero_reports_is_low_and_deterministic():
    session = ReportSession([])
    first = get_risk_meter(session, "area", 1, now=NOW)
    second = get_risk_meter(session, "area", 1, now=NOW)
    assert first == second
    assert (first.score, first.band, first.report_count) == (0.0, "low", 0)


def test_risk_meter_dismissed_evidence_contributes_zero():
    dismissed = report("user", reporter_id="device", status="unsafe")
    dismissed.verification_decision = "dismiss"
    meter = get_risk_meter(ReportSession([dismissed]), "area", 1, now=NOW)
    assert (meter.score, meter.band, meter.report_count) == (0.0, "low", 0)


def test_risk_meter_confirmed_evidence_is_critical():
    confirmed = report("user", reporter_id="device")
    confirmed.verification_decision = "confirm"
    meter = get_risk_meter(ReportSession([confirmed]), "area", 1, now=NOW)
    assert (meter.score, meter.band, meter.report_count) == (100.0, "critical", 1)
    assert resolve_reports([confirmed], latitude=12.9, longitude=77.5, now=NOW).status == "unsafe"


def test_risk_meter_band_boundaries():
    assert [risk_meter_band(score) for score in (0, 24.99, 25, 49.99, 50, 74.99, 75, 100)] == [
        "low", "low", "rising", "rising", "elevated", "elevated", "critical", "critical"
    ]


def test_stale_user_evidence_is_ignored_by_meter():
    stale = report("user", reporter_id="device", created_at=NOW.replace(hour=9, minute=59))
    meter = get_risk_meter(ReportSession([stale]), "area", 1, now=NOW)
    assert (meter.score, meter.report_count) == (0.0, 0)
