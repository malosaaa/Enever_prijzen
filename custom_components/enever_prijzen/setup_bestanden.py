import json
import os

manifest_data = {
    "domain": "enever_prijzen",
    "name": "Enever Energieprijzen",
    "config_flow": True,
    "version": "1.0.0",
    "dependencies": [],
    "integration_type": "service",
}

en_data = {
    "config": {
        "step": {
            "user": {
                "title": "Enever API",
                "data": {
                    "api_token": "API Token",
                    "stroom_provider": "Power Provider",
                    "gas_provider": "Gas Provider",
                    "scan_interval": "Scan Interval (s)",
                },
            }
        }
    },
    "entity": {
        "sensor": {
            "current_power": {"name": "Current Power Price"},
            "current_gas": {"name": "Current Gas Price"},
            "last_update": {"name": "Last Update"},
            "errors": {"name": "Errors"},
        }
    },
}

nl_data = {
    "config": {
        "step": {
            "user": {
                "title": "Enever API",
                "data": {
                    "api_token": "API Token",
                    "stroom_provider": "Stroom Leverancier",
                    "gas_provider": "Gas Leverancier",
                    "scan_interval": "Scan Interval (s)",
                },
            }
        }
    },
    "entity": {
        "sensor": {
            "current_power": {"name": "Actuele Stroomprijs"},
            "current_gas": {"name": "Actuele Gasprijs"},
            "last_update": {"name": "Laatste Update"},
            "errors": {"name": "Fouten"},
        }
    },
}


def create_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    translations_dir = os.path.join(current_dir, "translations")
    os.makedirs(translations_dir, exist_ok=True)
    with open(os.path.join(translations_dir, "en.json"), "w", encoding="utf-8") as f:
        json.dump(en_data, f, indent=2)
    with open(os.path.join(translations_dir, "nl.json"), "w", encoding="utf-8") as f:
        json.dump(nl_data, f, indent=2)
    print("✅ Klaar!")


if __name__ == "__main__":
    create_files()
