import pytest
from unittest.mock import patch
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.enever_prijzen.const import (
    DOMAIN,
    CONF_API_TOKEN,
    CONF_STROOM_PROVIDER,
    CONF_GAS_PROVIDER,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield


@pytest.mark.asyncio
async def test_config_flow_user_success(hass):
    """Test user flow initializes setup schema and provisions entry parameters successfully."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch("custom_components.enever_prijzen.async_setup_entry", return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_API_TOKEN: "secret_token_123",
                CONF_STROOM_PROVIDER: "EE",
                CONF_GAS_PROVIDER: "EE",
            },
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert "Enever" in result2["title"]
    assert result2["data"][CONF_API_TOKEN] == "secret_token_123"
    assert result2["options"][CONF_SCAN_INTERVAL] == DEFAULT_SCAN_INTERVAL


@pytest.mark.asyncio
async def test_config_flow_missing_token(hass):
    """Verify flow catches validation failures when required keys are omitted."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_API_TOKEN: "",
            CONF_STROOM_PROVIDER: "EE",
            CONF_GAS_PROVIDER: "EE",
        },
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"][CONF_API_TOKEN] == "required"


@pytest.mark.asyncio
async def test_options_flow(hass):
    """Verify standalone updating parameters process correctly through the options layer."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_TOKEN: "token",
            CONF_STROOM_PROVIDER: "EE",
            CONF_GAS_PROVIDER: "EE",
        },
        options={CONF_SCAN_INTERVAL: 3600},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_SCAN_INTERVAL: 7200,
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SCAN_INTERVAL] == 7200
