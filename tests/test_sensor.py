import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from custom_components.enever_prijzen.sensor import (
    EneverStroomSensor,
    EneverGasSensor,
    EneverStatusSensor,
)


@pytest.fixture
def mock_coordinator():
    coord = MagicMock()
    # Mocking the active current timeline context specifically matching May 20, 2026 at 17:00
    coord.data = {
        "stroom": [
            {"datum": "2026-05-20 16:00:00", "prijsEE": 0.12000},
            {"datum": "2026-05-20 17:00:00", "prijsEE": 0.18500},  # Active match hour
            {"datum": "2026-05-20 18:00:00", "prijsEE": 0.22000},
        ],
        "gas": [{"datum": "2026-05-20 00:00:00", "prijsEE": 1.15430}],
    }
    coord.last_update_success_timestamp = "2026-05-20T17:01:00+00:00"
    coord.error_count = 0
    return coord


def test_stroom_sensor_time_matching(mock_coordinator):
    """Verify that electricity sensor identifies the correct current hour block row properly."""
    sensor = EneverStroomSensor(mock_coordinator, "EE")

    assert sensor.unique_id == "enever_energieprijzen_stroom"
    assert sensor.native_unit_of_measurement == "EUR/kWh"

    # Set system time context directly to match our 17:00 row entry
    mock_now = datetime(2026, 5, 20, 17, 30, 0)
    with patch(
        "custom_components.enever_prijzen.sensor.dt_util.now", return_value=mock_now
    ):
        assert sensor.state == 0.18500

    # Test attributes list map matching history sets
    attrs = sensor.extra_state_attributes
    assert attrs["provider"] == "EasyEnergy"
    assert len(attrs["all_prices"]) == 3


def test_gas_sensor_and_empty_fallbacks(mock_coordinator):
    """Verify gas prices evaluate from base lists and fall back cleanly on empty states."""
    gas_sensor = EneverGasSensor(mock_coordinator, "EE")
    assert gas_sensor.state == 1.15430
    assert gas_sensor.native_unit_of_measurement == "EUR/m³"

    # Verify fallback triggers safely
    mock_coordinator.data = {"stroom": [], "gas": []}
    stroom_sensor = EneverStroomSensor(mock_coordinator, "EE")
    assert stroom_sensor.state is None
    assert gas_sensor.state is None


def test_status_diagnostic_sensors(mock_coordinator):
    """Verify diagnostic sensor arrays accurately display operational states."""
    update_sensor = EneverStatusSensor(
        mock_coordinator, "last_update", "Laatste Update", "mdi:clock", "timestamp"
    )
    error_sensor = EneverStatusSensor(
        mock_coordinator, "errors", "Fouten", "mdi:alert", None
    )

    assert update_sensor.state == "2026-05-20T17:01:00+00:00"
    assert error_sensor.state == 0

    mock_coordinator.error_count = 3
    assert error_sensor.state == 3
