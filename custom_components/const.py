DOMAIN = "enever_prijzen"
CONF_API_TOKEN = "api_token"
CONF_STROOM_PROVIDER = "stroom_provider"
CONF_GAS_PROVIDER = "gas_provider"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 3600 # 1x per uur updaten is genoeg

PROVIDERS = {
    "ANWB": "ANWB Energie",
    "BE": "Budget Energie",
    "CB": "Coolblue Energie",
    "ED": "Energiedirect",
    "EE": "EasyEnergy",
    "EG": "Energiek",
    "EN": "Eneco",
    "ES": "Essent",
    "EVO": "Energie van Ons",
    "EZ": "Energy Zero",
    "FR": "Frank Energie",
    "GSL": "Groenestroom Lokaal",
    "HE": "Hegg Energy",
    "IN": "Innova Energie",
    "MDE": "Mijndomein Energie",
    "NE": "NextEnergy",
    "PE": "Pure Energie",
    "QU": "Quatt",
    "SS": "SamSam",
    "TI": "Tibber",
    "VDB": "Vandebron",
    "VF": "Vattenfall",
    "VON": "Vrij op naam",
    "WE": "Wout Energie",
    "ZG": "ZonderGas",
    "ZP": "Zonneplan"
}

PLATFORMS = ["sensor"]