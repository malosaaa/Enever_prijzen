# 🇳🇱 Enever Energieprijzen voor Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)][hacs]
[![Project Maintenance][maintenance_badge]](https://github.com/Malosaaa/ha-p2000)

Een efficiënte en robuuste Home Assistant integratie die de actuele, all-in dynamische stroom- en gasprijzen ophaalt via de Enever.nl API. Perfect als vervanging voor verdwenen API's (zoals EasyEnergy) en essentieel voor het slim sturen van je apparaten op basis van de daadwerkelijke consumentenprijzen.

## ✨ Functionaliteiten

* **Ondersteuning voor 26 Leveranciers:** Kies direct jouw aanbieder, waaronder EasyEnergy, Frank Energie, ANWB, Tibber, NextEnergy, Zonneplan en nog veel meer.
* **All-in Prijzen:** Toont direct de échte consumentenprijs (inclusief energiebelasting, inkoopkosten en BTW).
* **Smart Cache Booting:** Laadt data na een herstart direct in vanaf de lokale schijf voor een bliksemsnelle opstarttijd zonder API-limieten te raken.
* **Stroom & Gas:** Haalt in één efficiënte achtergrondtaak zowel de uurprijzen voor stroom (vandaag én morgen) als de dagprijzen voor gas op.
* **Geoptimaliseerd:** Geen vertragingen in je Home Assistant dankzij asynchrone achtergrondverwerking.

## 📥 Installatie via HACS

1. Ga in Home Assistant naar **HACS** > **Integraties**.
2. Klik rechtsboven op de drie puntjes en kies **Aangepaste repositories** (Custom repositories).
3. Voeg de URL van deze repository toe en kies als categorie **Integratie**.
4. Klik op toevoegen, zoek naar *Enever Energieprijzen* in HACS en klik op **Download**.
5. Herstart Home Assistant.

## ⚙️ Configuratie

1. Zorg dat je een (gratis) API token hebt van [Enever.nl](https://enever.nl/).
2. Ga in Home Assistant naar **Instellingen** > **Apparaten & Diensten**.
3. Klik rechtsonder op **+ Integratie toevoegen**.
4. Zoek naar **Enever Energieprijzen**.
5. Vul je API token in en selecteer uit de dropdown-menu's jouw specifieke stroom- en gasleverancier.

## 📊 Dashboard Kaart (Markdown)

Deze dynamische Markdown-kaart combineert gas en stroom in één prachtig overzicht, past automatisch de kleuren aan en geeft een handig advies op basis van het huidige stroomtarief.

```yaml
type: markdown
content: >-
  {% set entity_power = 'sensor.enever_energieprijzen_current_power_price' %} {%
  set entity_gas = 'sensor.enever_energieprijzen_current_gas_price' %}

  {% set power_prices = state_attr(entity_power, 'all_prices') %} {% set
  prov_power = state_attr(entity_power, 'provider') %} {% set prov_gas =
  state_attr(entity_gas, 'provider') %}

  ## ⚡ Actuele Energieprijzen

  <div style="display: flex; gap: 10px; margin-bottom: 15px;">

  {# --- GAS BLOK --- #} {% if states(entity_gas) not in ['unknown',
  'unavailable'] %} {% set gas_price = states(entity_gas) | float(0) %} {% set
  format_gas = "{:0.2f}".format(gas_price) | replace('.', ',') %} <div
  style="flex: 1; background-color: rgba(33, 150, 243, 0.1); padding: 15px;
  border-radius: 10px; text-align: center; border-bottom: 4px solid #2196F3;">
  <div style="font-size: 1em; opacity: 0.8;">🔥 Gas ({{ prov_gas }})</div> <div
  style="font-size: 2.2em; font-weight: bold; color: #2196F3; line-height:
  1.2;"> &euro; {{ format_gas }} </div> <div style="font-size: 0.75em; opacity:
  0.6;">per m³ (all-in)</div> </div> {% endif %}

  {# --- STROOM BLOK --- #} {% if states(entity_power) not in ['unknown',
  'unavailable'] %} {% set power_price = states(entity_power) | float(0) %} {%
  set format_power = "{:0.2f}".format(power_price) | replace('.', ',') %}

  {% set color_main = '#00C853' %} {% set advies = 'Prijzen zijn erg laag!
  Perfect moment voor groot stroomverbruik.' %} {% set icon = '🔥' %}

  {% if power_price >= 0.18 %}{% set color_main = '#8BC34A' %}{% set advies =
  'Gunstig tarief. Een prima moment om apparaten aan te zetten.' %}{% set icon =
  '✅' %}{% endif %} {% if power_price >= 0.24 %}{% set color_main = '#FF9800'
  %}{% set advies = 'Prijzen zijn gemiddeld. Geen bijzonderheden.' %}{% set icon
  = '⚖️' %}{% endif %} {% if power_price >= 0.28 %}{% set color_main = '#F44336'
  %}{% set advies = 'Prijzen zijn hoog! Stel zware apparaten zoals de wasmachine
  even uit.' %}{% set icon = '⚠️' %}{% endif %}

  <div style="flex: 1; background-color: {{ color_main }}15; padding: 15px;
  border-radius: 10px; text-align: center; border-bottom: 4px solid {{
  color_main }};"> <div style="font-size: 1em; opacity: 0.8;">⚡ Stroom ({{
  prov_power }})</div> <div style="font-size: 2.2em; font-weight: bold; color:
  {{ color_main }}; line-height: 1.2;"> &euro; {{ format_power }} </div> <div
  style="font-size: 0.75em; opacity: 0.6;">per kWh (all-in)</div> </div> {%
  endif %}

  </div>

  {# --- ADVIES BLOK --- #} {% if states(entity_power) not in ['unknown',
  'unavailable'] %} <div style="background-color: {{ color_main }}15; padding:
  12px; border-left: 5px solid {{ color_main }}; border-radius: 5px;
  margin-bottom: 20px; font-size: 0.9em;"> <b>{{ icon }} Slim Advies:</b> {{
  advies }} </div> {% endif %}

  --- <br>

  {# --- TABELLEN --- #} {% if power_prices %} ### 🕒 Verwachte stroomprijzen
  (komende 8 uur) <table style="width: 100%; text-align: left; border-collapse:
  collapse; font-size: 0.9em;"> <tr> <th style="border-bottom: 1px solid
  rgba(128, 128, 128, 0.3); padding: 8px 0;">Tijd</th> <th style="border-bottom:
  1px solid rgba(128, 128, 128, 0.3); padding: 8px 0;">Prijs (all-in)</th> </tr>
  {% set ns = namespace(found=0) %} {% for item in power_prices %} {% set
  item_time = as_datetime(item.datum) | as_local %} {% if item_time >=
  now().replace(minute=0, second=0, microsecond=0) and ns.found < 8 %}

  {% set val = item.prijs | float(0) %} {% set format_item =
  "{:0.2f}".format(val) | replace('.', ',') %} {% set color = '#00C853' %} {% if
  val >= 0.18 %}{% set color = '#8BC34A' %}{% endif %} {% if val >= 0.24 %}{%
  set color = '#FF9800' %}{% endif %} {% if val >= 0.28 %}{% set color =
  '#F44336' %}{% endif %}

  {% set time_str = item_time.strftime('%H:%M') %} {% if item_time.day !=
  now().day %}
    {% set time_str = 'Morgen ' ~ item_time.strftime('%H:%M') %}
  {% endif %}

  <tr> <td style="padding: 8px 0;">{{ time_str }}</td> <td style="padding: 8px
  0; color: {{ color }}; font-weight: bold;">&euro; {{ format_item }}</td> </tr>
  {% set ns.found = ns.found + 1 %} {% endif %} {% endfor %} </table>

  <br>

  ### 📅 Prijzen voor Morgen {% set tomorrow = (now() + timedelta(days=1)).day
  %} {% set ns_morgen = namespace(found=0) %}

  {% for item in power_prices %} {% set item_time = as_datetime(item.datum) |
  as_local %} {% if item_time.day == tomorrow %} {% set ns_morgen.found = 1 %}
  {% endif %} {% endfor %}

  {% if ns_morgen.found == 1 %} <table style="width: 100%; text-align: left;
  border-collapse: collapse; font-size: 0.9em;"> <tr> <th style="border-bottom:
  1px solid rgba(128, 128, 128, 0.3); padding: 8px 0;">Tijd</th> <th
  style="border-bottom: 1px solid rgba(128, 128, 128, 0.3); padding: 8px
  0;">Prijs (all-in)</th> </tr> {% for item in power_prices %} {% set item_time
  = as_datetime(item.datum) | as_local %} {% if item_time.day == tomorrow %} {%
  set val = item.prijs | float(0) %} {% set format_item = "{:0.2f}".format(val)
  | replace('.', ',') %} {% set color = '#00C853' %} {% if val >= 0.18 %}{% set
  color = '#8BC34A' %}{% endif %} {% if val >= 0.24 %}{% set color = '#FF9800'
  %}{% endif %} {% if val >= 0.28 %}{% set color = '#F44336' %}{% endif %} <tr>
  <td style="padding: 8px 0;">{{ item_time.strftime('%H:%M') }}</td> <td
  style="padding: 8px 0; color: {{ color }}; font-weight: bold;">&euro; {{
  format_item }}</td> </tr> {% endif %} {% endfor %} </table> {% else %} <div
  style="opacity: 0.7; font-style: italic; padding: 10px 0;"> De prijzen voor
  morgen zijn momenteel nog niet bekend. </div> {% endif %}

  {% else %} ⏳ Wachten op gegevens... {% endif %}

```
[hacs]: https://hacs.xyz
[hacs_badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[maintenance_badge]: https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge





