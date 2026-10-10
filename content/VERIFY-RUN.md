# Content pilot verification run (v2)

Date: 2026-10-10
Command: `python3 scripts/verify-content-pilot.py`
Result: **PASS**

## Counts

```json
{
  "brands": 10,
  "organizations": 149,
  "locations": 151,
  "services": 228,
  "products": 12,
  "variants": 12,
  "evidence": 231,
  "explainers": 6,
  "comparisons": 3,
  "articleMarkdown": 9,
  "brandLinks": 70,
  "cities": [
    "Ajka",
    "Baja",
    "Balassagyarmat",
    "Balatonfüred",
    "Biatorbágy",
    "Budakeszi",
    "Budapest",
    "Budaörs",
    "Bátonyterenye",
    "Békéscsaba",
    "Cegléd",
    "Debrecen",
    "Dunakeszi",
    "Dunaújváros",
    "Eger",
    "Esztergom",
    "Gyula",
    "Gyömrő",
    "Gyöngyös",
    "Győr",
    "Göd",
    "Gödöllő",
    "Hatvan",
    "Hódmezővásárhely",
    "Jászberény",
    "Kalocsa",
    "Kaposvár",
    "Kazincbarcika",
    "Kecskemét",
    "Keszthely",
    "Kiskunfélegyháza",
    "Komárom",
    "Körmend",
    "Makó",
    "Mezőkövesd",
    "Miskolc",
    "Nagykanizsa",
    "Nagykáta",
    "Nyíregyháza",
    "Orosháza",
    "Pápa",
    "Pécs",
    "Salgótarján",
    "Siófok",
    "Sopron",
    "Szeged",
    "Szekszárd",
    "Szentendre",
    "Szentes",
    "Szolnok",
    "Szombathely",
    "Székesfehérvár",
    "Tatabánya",
    "Tiszafüred",
    "Tiszaújváros",
    "Tát",
    "Tótkomlós",
    "Törökbálint",
    "Velence",
    "Veresegyház",
    "Veszprém",
    "Vác",
    "Zalaegerszeg",
    "Érd",
    "Ózd"
  ]
}
```

## Status tallies

```json
{
  "brands": {
    "ellenőrzött": 9,
    "előkészített": 1
  },
  "locations": {
    "ellenőrzött": 151
  },
  "variants": {
    "ellenőrzött": 10,
    "előkészített": 2
  },
  "explainers": {
    "ellenőrzött": 6
  },
  "comparisons": {
    "ellenőrzött": 3
  },
  "evidence": {
    "ellenőrzött": 227,
    "előkészített": 3,
    "hiányos": 1
  },
  "services": 228
}
```

## Checks

- PASS: `required_files` — all present
- PASS: `count_brands_at_least_10` — 10
- PASS: `count_locations_at_least_20` — 151
- PASS: `count_variants_12` — 12
- PASS: `count_explainers_6` — 6
- PASS: `count_comparisons_3` — 3
- PASS: `count_comparison_groups_3` — 3
- PASS: `cities_at_least_6_total` — ['Ajka', 'Baja', 'Balassagyarmat', 'Balatonfüred', 'Biatorbágy', 'Budakeszi', 'Budapest', 'Budaörs', 'Bátonyterenye', 'Békéscsaba', 'Cegléd', 'Debrecen', 'Dunakeszi', 'Dunaújváros', 'Eger', 'Esztergom', 'Gyula', 'Gyömrő', 'Gyöngyös', 'Győr', 'Göd', 'Gödöllő', 'Hatvan', 'Hódmezővásárhely', 'Jászberény', 'Kalocsa', 'Kaposvár', 'Kazincbarcika', 'Kecskemét', 'Keszthely', 'Kiskunfélegyháza', 'Komárom', 'Körmend', 'Makó', 'Mezőkövesd', 'Miskolc', 'Nagykanizsa', 'Nagykáta', 'Nyíregyháza', 'Orosháza', 'Pápa', 'Pécs', 'Salgótarján', 'Siófok', 'Sopron', 'Szeged', 'Szekszárd', 'Szentendre', 'Szentes', 'Szolnok', 'Szombathely', 'Székesfehérvár', 'Tatabánya', 'Tiszafüred', 'Tiszaújváros', 'Tát', 'Tótkomlós', 'Törökbálint', 'Velence', 'Veresegyház', 'Veszprém', 'Vác', 'Zalaegerszeg', 'Érd', 'Ózd']
- PASS: `cities_non_budapest_at_least_5` — ['Ajka', 'Baja', 'Balassagyarmat', 'Balatonfüred', 'Biatorbágy', 'Budakeszi', 'Budaörs', 'Bátonyterenye', 'Békéscsaba', 'Cegléd', 'Debrecen', 'Dunakeszi', 'Dunaújváros', 'Eger', 'Esztergom', 'Gyula', 'Gyömrő', 'Gyöngyös', 'Győr', 'Göd', 'Gödöllő', 'Hatvan', 'Hódmezővásárhely', 'Jászberény', 'Kalocsa', 'Kaposvár', 'Kazincbarcika', 'Kecskemét', 'Keszthely', 'Kiskunfélegyháza', 'Komárom', 'Körmend', 'Makó', 'Mezőkövesd', 'Miskolc', 'Nagykanizsa', 'Nagykáta', 'Nyíregyháza', 'Orosháza', 'Pápa', 'Pécs', 'Salgótarján', 'Siófok', 'Sopron', 'Szeged', 'Szekszárd', 'Szentendre', 'Szentes', 'Szolnok', 'Szombathely', 'Székesfehérvár', 'Tatabánya', 'Tiszafüred', 'Tiszaújváros', 'Tát', 'Tótkomlós', 'Törökbálint', 'Velence', 'Veresegyház', 'Veszprém', 'Vác', 'Zalaegerszeg', 'Érd', 'Ózd']
- PASS: `unique_ids_brands` — ok
- PASS: `unique_ids_locations` — ok
- PASS: `unique_ids_services` — ok
- PASS: `unique_ids_products` — ok
- PASS: `unique_ids_variants` — ok
- PASS: `unique_ids_evidence` — ok
- PASS: `brand_slugs_unique` — ['cube', 'giant', 'trek', 'specialized', 'merida', 'scott', 'cannondale', 'gepida', 'neuzer', 'ktm-bike']
- PASS: `products_brandId_resolve` — ok
- PASS: `variants_productId_resolve` — ok
- PASS: `locations_organizationId_resolve` — ok
- PASS: `services_locationId_resolve` — ok
- PASS: `services_have_sourceUrl` — ok
- PASS: `brand_links_and_location_evidence` — ok linked=70
- PASS: `brand_links_at_least_8` — 70
- PASS: `rekord_szerviz_not_on_locations` — ok
- PASS: `variant_evidence_supports_and_titles` — ok
- PASS: `location_evidence_pageTitles` — ok
- PASS: `status_vocabulary` — ok
- PASS: `publishable_brands_at_least_10` — 10
- PASS: `publishable_variants_12` — 12
- PASS: `article_markdown_files_9` — ['e-bike-tomeg-magyarazo.md', 'e-bike-motor-magyarazo.md', 'e-bike-nyomatek-nm-magyarazo.md', 'osszehasonlitas-varosi-trekking-e-bike.md', 'e-bike-szervizhatter-magyarazo.md', 'e-bike-hatotav-magyarazo.md', 'e-bike-akkukapacitas-wh-magyarazo.md', 'osszehasonlitas-varosi-komfort-e-bike.md', 'osszehasonlitas-e-mtb.md']
- PASS: `article_md_matches_json_slugs` — ok
- PASS: `articles_evidence_and_md_parity` — ok
- PASS: `comparison_group_renamed_city_comfort` — ['cmp-city-comfort', 'cmp-city-trekking', 'cmp-e-mtb']
- PASS: `old_compact_group_removed` — ['cmp-city-comfort', 'cmp-city-trekking', 'cmp-e-mtb']
- PASS: `trek_weight_phrase_in_comparison` — ok
- PASS: `explainer_wh_has_bosch_batteries` — ['ev-bosch-batteries', 'ev-bosch-range-assistant']
- PASS: `explainer_range_has_range_assistant` — ['ev-bosch-range-assistant', 'ev-bosch-batteries', 'ev-bosch-help-range-nyon']
- PASS: `variants_cover_at_least_4_brands` — ['brand-cube', 'brand-gepida', 'brand-giant', 'brand-merida', 'brand-specialized', 'brand-trek']
- PASS: `comparison_groups_valid` — [{'id': 'cmp-city-trekking', 'n': 4, 'ok': True}, {'id': 'cmp-e-mtb', 'n': 4, 'ok': True}, {'id': 'cmp-city-comfort', 'n': 4, 'ok': True}]

Conflicts recorded: 6
Held back: 4

Raw JSON: `content/VERIFY-RUN-RESULT.json`
