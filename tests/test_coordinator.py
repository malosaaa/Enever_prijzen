import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enever_prijzen.const import DOMAIN
from custom_components.enever_prijzen.coordinator import EneverCoordinator

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield

@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.save_cache = MagicMock()
    return cache

@pytest.fixture
def mock_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={"api_token": "test_token", "stroom_provider": "EE", "gas_provider": "EE"},
        options={"scan_interval": 3600}
    )


@pytest.mark.asyncio
@patch("custom_components.enever_prijzen.coordinator.async_get_clientsession")
async def test_coordinator_successful_refresh(mock_get_session, hass: HomeAssistant, mock_entry, mock_cache):
    """Verify parsing and caching loop mechanics sort prices correctly from API calls."""
    coord = EneverCoordinator(hass, mock_entry, mock_cache)
    coord._is_first_run = False

    # Set up mock API responses
    mock_stroom_vandaag = AsyncMock()
    mock_stroom_vandaag.status = 200
    mock_stroom_vandaag.json.return_value = {"data": [{"datum": "2026-05-20 18:00:00", "prijsEE": 0.20}]}
    
    mock_stroom_morgen = AsyncMock()
    mock_stroom_morgen.status = 200
    mock_stroom_morgen.json.return_value = {"data": [{"datum": "2026-05-21 00:00:00", "prijsEE": 0.25}]}

    mock_gas_vandaag = AsyncMock()
    mock_gas_vandaag.status = 200
    mock_gas_vandaag.json.return_value = {"data": [{"datum": "2026-05-20 00:00:00", "prijsEE": 1.10}]}

    mock_session = MagicMock()
    mock_session.get.side_effect = [
        MagicMock(__aenter__=AsyncMock(return_value=mock_stroom_vandaag)),
        MagicMock(__aenter__=AsyncMock(return_value=mock_stroom_morgen)),
        MagicMock(__aenter__=AsyncMock(return_value=mock_gas_vandaag))
    ]
    mock_get_session.return_value = mock_session

    result = await coord._async_update_data()
    assert len(result["stroom"]) == 2
    assert len(result["gas"]) == 1
    assert coord.error_count == 0
    mock_cache.save_cache.assert_called_once()


@pytest.mark.asyncio
@patch("custom_components.enever_prijzen.coordinator.async_get_clientsession")
async def test_coordinator_api_limit_hibernation(mock_get_session, hass: HomeAssistant, mock_entry, mock_cache):
    """Verify when Code 6 returns, hibernation is engaged and queries stop entirely."""
    coord = EneverCoordinator(hass, mock_entry, mock_cache)
    coord._is_first_run = False
    coord.last_data = {"stroom": [{"cached": True}], "gas": []}

    # Code 6 triggers hibernation
    mock_limit_resp = AsyncMock()
    mock_limit_resp.status = 200
    mock_limit_resp.json.return_value = {"code": "6", "status": "Api limit reached"}

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_limit_resp
    mock_get_session.return_value = mock_session

    # 1. First poll hits the limit block and initiates winter hibernation
    current_month = datetime.now().month
    result1 = await coord._async_update_data()
    assert coord.limit_reached_month == current_month
    assert result1 == {"stroom": [{"cached": True}], "gas": []}

    # 2. Subsequent polls in the same month immediately bypass network queries and return cache
    mock_get_session.reset_mock()
    result2 = await coord._async_update_data()
    mock_get_session.assert_not_called()
    assert result2 == {"stroom": [{"cached": True}], "gas": []}


@pytest.mark.asyncio
@patch("custom_components.enever_prijzen.coordinator.async_get_clientsession")
async def test_coordinator_exception_handling(mock_get_session, hass: HomeAssistant, mock_entry, mock_cache):
    """Ensure network failures are captured cleanly and error telemetry registers."""
    coord = EneverCoordinator(hass, mock_entry, mock_cache)
    coord._is_first_run = False
    coord.last_data = {"stroom": [], "gas": []}

    mock_get_session.side_effect = Exception("Connection Timeout")
    
    result = await coord._async_update_data()
    assert coord.error_count == 1
    assert result == {"stroom": [], "gas": []}
