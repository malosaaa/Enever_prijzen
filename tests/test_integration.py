import pytest
import respx
from httpx import Response
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enever_prijzen.const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_STROOM_PROVIDER,
    CONF_GAS_PROVIDER,
    CONF_SCAN_INTERVAL,
)


# =========================================================================
# 1. FLOW ENGINE VALIDATION SECTOR
# =========================================================================


@pytest.mark.asyncio
async def test_config_flow_lifecycle(hass: HomeAssistant):
    """Test initial flow initialization setup saves entries with target schemas."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_API_TOKEN: "test-token-12345",
            CONF_STROOM_PROVIDER: "EE",
            CONF_GAS_PROVIDER: "FR",
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_API_TOKEN] == "test-token-12345"
    assert result2["data"][CONF_STROOM_PROVIDER] == "EE"


@pytest.mark.asyncio
async def test_options_flow_interval_update(hass: HomeAssistant):
    """Test modification schemas alter polling loop time schedules securely."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Enever Prices",
        data={
            CONF_API_TOKEN: "mock-token",
            CONF_STROOM_PROVIDER: "EE",
            CONF_GAS_PROVIDER: "EE",
        },
        options={CONF_SCAN_INTERVAL: 3600},
        entry_id="enever_options_test",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: 1800},
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_SCAN_INTERVAL] == 1800


# =========================================================================
# 2. ENDPOINT INTERCEPTION & STATE SECTOR
# =========================================================================


@pytest.mark.asyncio
@respx.mock
async def test_coordinator_sensor_extraction_loop(hass: HomeAssistant):
    """Test aiohttp scraping routes map payloads to historical attribute dictionaries."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Enever Test Instance",
        data={
            CONF_API_TOKEN: "valid-token",
            CONF_STROOM_PROVIDER: "EE",
            CONF_GAS_PROVIDER: "EE",
        },
        entry_id="enever_live_test",
    )
    entry.add_to_hass(hass)

    # Generate an active dynamic date matching the exact hour string requested by sensor filters
    current_time_str = dt_util.now().strftime("%Y-%m-%d %H:%M:%S")

    # Intercept each external PHP API file request smoothly
    respx.get("https://enever.nl/apiv3/stroomprijs_vandaag.php?token=valid-token").mock(
        return_value=Response(
            200, json={"data": [{"datum": current_time_str, "prijsEE": "0.2450"}]}
        )
    )
    respx.get("https://enever.nl/apiv3/stroomprijs_morgen.php?token=valid-token").mock(
        return_value=Response(200, json={"data": []})
    )
    respx.get("https://enever.nl/apiv3/gasprijs_vandaag.php?token=valid-token").mock(
        return_value=Response(
            200, json={"data": [{"datum": current_time_str, "prijsEE": "1.1500"}]}
        )
    )

    # Ensure local file system calls during initial empty cache reading do not halt setup processing
    with (
        patch(
            "custom_components.enever_prijzen.cache.EneverCache.load_cache",
            return_value={"stroom": [], "gas": []},
        ),
        patch("custom_components.enever_prijzen.cache.EneverCache.save_cache"),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Verify sensor state values match float conversion calculations
    stroom_sensor = hass.states.get("sensor.enever_energieprijzen_stroom")
    assert stroom_sensor is not None
    assert stroom_sensor.state == "0.245"

    gas_sensor = hass.states.get("sensor.enever_energieprijzen_gas")
    assert gas_sensor is not None
    assert gas_sensor.state == "1.15"


# =========================================================================
# 3. SAFETY CONTROLLER SECTOR (HIBERNATION WINTERSLAAP)
# =========================================================================


@pytest.mark.asyncio
@respx.mock
async def test_api_limit_hibernation_safeguard(hass: HomeAssistant):
    """Test engine enters automatic hibernation upon capturing limit error notice payloads."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Enever Safety Check",
        data={
            CONF_API_TOKEN: "limited-token",
            CONF_STROOM_PROVIDER: "EE",
            CONF_GAS_PROVIDER: "EE",
        },
        entry_id="enever_limit_test",
    )
    entry.add_to_hass(hass)

    # Simulate hitting your limit by forcing code 6 response parameters from the remote server
    respx.get(
        "https://enever.nl/apiv3/stroomprijs_vandaag.php?token=limited-token"
    ).mock(
        return_value=Response(200, json={"code": "6", "message": "API limit reached"})
    )

    with patch(
        "custom_components.enever_prijzen.cache.EneverCache.load_cache",
        return_value={"stroom": [], "gas": []},
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Ensure persistent notifications are deployed onto the user's interface queue
    notifications = hass.data.get("persistent_notification")
    assert "enever_api_limit" in notifications
