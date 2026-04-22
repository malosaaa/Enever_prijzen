from datetime import datetime
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import dt as dt_util
from .const import DOMAIN, PROVIDERS

# Koppel de gekozen naam aan de code in de Enever API
PROVIDER_KEYS = {
    "ANWB": "prijsANWB", "BE": "prijsBE", "CB": "prijsCB", "ED": "prijsED",
    "EE": "prijsEE", "EG": "prijsEG", "EN": "prijsEN", "ES": "prijsES",
    "EVO": "prijsEVO", "EZ": "prijsEZ", "FR": "prijsFR", "GSL": "prijsGSL",
    "HE": "prijsHE", "IN": "prijsIN", "MDE": "prijsMDE", "NE": "prijsNE",
    "PE": "prijsPE", "QU": "prijsQU", "SS": "prijsSS", "TI": "prijsTI",
    "VDB": "prijsVDB", "VF": "prijsVF", "VON": "prijsVON", "WE": "prijsWE",
    "ZG": "prijsZG", "ZP": "prijsZP"
}

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    stroom_prov = entry.data.get("stroom_provider", "EE")
    gas_prov = entry.data.get("gas_provider", "EE")
    
    async_add_entities([
        EneverStroomSensor(coordinator, stroom_prov),
        EneverGasSensor(coordinator, gas_prov),
        EneverStatusSensor(coordinator, "last_update", "Laatste Update", "mdi:clock-outline", SensorDeviceClass.TIMESTAMP),
        EneverStatusSensor(coordinator, "errors", "Fouten", "mdi:alert-circle-outline", None)
    ])

class EneverBaseEntity(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._device_id = "enever_energieprijzen"
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name="Enever Energieprijzen",
            manufacturer="Enever",
            model="Dynamische Tarieven",
        )

class EneverStroomSensor(EneverBaseEntity):
    def __init__(self, coordinator, provider):
        super().__init__(coordinator)
        self._provider = provider
        self._api_key = PROVIDER_KEYS.get(provider, "prijsEE")
        self._attr_translation_key = "current_power"
        self._attr_unique_id = f"{self._device_id}_stroom"
        self._attr_icon = "mdi:lightning-bolt"
        self._attr_native_unit_of_measurement = "EUR/kWh"

    @property
    def state(self):
        stroom_data = self.coordinator.data.get("stroom", [])
        if not stroom_data: return None
        
        now = dt_util.now()
        for item in stroom_data:
            try:
                dt = datetime.fromisoformat(item["datum"])
                if dt.year == now.year and dt.month == now.month and dt.day == now.day and dt.hour == now.hour:
                    val = item.get(self._api_key)
                    return float(val) if val is not None else None
            except Exception: continue
        return None

    @property
    def extra_state_attributes(self):
        stroom_data = self.coordinator.data.get("stroom", [])
        history = []
        for item in stroom_data:
            val = item.get(self._api_key)
            if val is not None:
                history.append({
                    "datum": item.get("datum"),
                    "prijs": float(val)
                })
        return {"provider": PROVIDERS.get(self._provider, self._provider), "all_prices": history}

class EneverGasSensor(EneverBaseEntity):
    def __init__(self, coordinator, provider):
        super().__init__(coordinator)
        self._provider = provider
        self._api_key = PROVIDER_KEYS.get(provider, "prijsEE")
        self._attr_translation_key = "current_gas"
        self._attr_unique_id = f"{self._device_id}_gas"
        self._attr_icon = "mdi:fire"
        self._attr_native_unit_of_measurement = "EUR/m³"

    @property
    def state(self):
        gas_data = self.coordinator.data.get("gas", [])
        if not gas_data: return None
        
        try:
            val = gas_data[0].get(self._api_key)
            return float(val) if val is not None else None
        except Exception: return None

    @property
    def extra_state_attributes(self):
        return {"provider": PROVIDERS.get(self._provider, self._provider)}

class EneverStatusSensor(EneverBaseEntity):
    def __init__(self, coordinator, key, name, icon, dev_class):
        super().__init__(coordinator)
        self._attr_translation_key = key
        self._attr_unique_id = f"{self._device_id}_{key}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = icon
        if dev_class: self._attr_device_class = dev_class

    @property
    def state(self):
        if self._attr_translation_key == "last_update":
            return getattr(self.coordinator, "last_update_success_timestamp", None)
        return getattr(self.coordinator, "error_count", 0)