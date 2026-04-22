import asyncio
import os
from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_TOKEN

_LOGGER = logging.getLogger(__name__)

class EneverCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, config_entry, cache_module):
        self.hass = hass
        self.api_token = config_entry.data[CONF_API_TOKEN]
        self.stroom_provider = config_entry.data.get("stroom_provider", "easyEnergy")
        self.gas_provider = config_entry.data.get("gas_provider", "easyEnergy")
        self.cache = cache_module
        
        # We slaan stroom en gas apart op in de dictionary
        self.last_data = {"stroom": [], "gas": []} 
        self.error_count = 0
        self.last_update_success_timestamp = None
        self._is_first_run = True
        
        scan_interval = config_entry.options.get("scan_interval", 3600)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=scan_interval))

    async def _async_update_data(self):
        if self._is_first_run and (self.last_data.get("stroom") or self.last_data.get("gas")):
            self._is_first_run = False
            _LOGGER.debug("Eerste run: Enever Download overgeslagen, cache gebruikt.")
            return self.last_data
            
        self._is_first_run = False
        session = async_get_clientsession(self.hass)
        
        urls = {
            "stroom_vandaag": f"https://enever.nl/apiv3/stroomprijs_vandaag.php?token={self.api_token}",
            "stroom_morgen": f"https://enever.nl/apiv3/stroomprijs_morgen.php?token={self.api_token}",
            "gas_vandaag": f"https://enever.nl/apiv3/gasprijs_vandaag.php?token={self.api_token}"
        }
        
        results = {"stroom": [], "gas": []}
        
        try:
            # 1. Haal Stroom Vandaag op
            async with session.get(urls["stroom_vandaag"]) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "data" in data:
                        results["stroom"].extend(data["data"])
                        
            # 2. Haal Stroom Morgen op (deze is in de ochtend nog leeg, we negeren evt fouten)
            async with session.get(urls["stroom_morgen"]) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "data" in data and isinstance(data["data"], list):
                        results["stroom"].extend(data["data"])
                        
            # 3. Haal Gas Vandaag op
            async with session.get(urls["gas_vandaag"]) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "data" in data:
                        results["gas"].extend(data["data"])

            # Sorteer alles netjes op datum
            if results["stroom"]:
                results["stroom"] = sorted(results["stroom"], key=lambda x: x.get("datum", ""))
            if results["gas"]:
                results["gas"] = sorted(results["gas"], key=lambda x: x.get("datum", ""))

            if results["stroom"] or results["gas"]:
                self.last_data = results
                await self.hass.async_add_executor_job(self.cache.save_cache, results)
                self.error_count = 0
                self.last_update_success_timestamp = dt_util.utcnow()
            else:
                self.error_count += 1
                
            return self.last_data
            
        except Exception as err:
            self.error_count += 1
            _LOGGER.error("Update mislukt voor Enever: %s", err)
            return self.last_data