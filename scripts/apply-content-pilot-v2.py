#!/usr/bin/env python3
"""Apply content-pilot v2 structural fixes (no invented brand/model facts)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ACCESS = "2026-10-10"
NA = "Nincs ellenőrzött adatunk"
DISCLAIMER = (
    "A márka forgalmazása nem jelenti automatikusan, hogy egy adott modell "
    "raktáron van, vagy kipróbálható."
)

BRAND_NAME_TO_ID = {
    "cube": "brand-cube",
    "giant": "brand-giant",
    "trek": "brand-trek",
    "specialized": "brand-specialized",
    "merida": "brand-merida",
    "scott": "brand-scott",
    "cannondale": "brand-cannondale",
    "gepida": "brand-gepida",
    "neuzer": "brand-neuzer",
    "ktm": "brand-ktm",
    "ktm bike industries": "brand-ktm",
}

# Location evidence page titles (from research / known page purpose)
LOC_EV_TITLES = {
    "ev-01": "Bemutatótermünk – Gepida",
    "ev-02": "Kapcsolat – Futurebike / Gepida Store",
    "ev-03": "Kerékpár szerviz – Futurebike",
    "ev-04": "BringaBoard Kerékpár Szaküzlet",
    "ev-05": "Bringavilág Kerékpárüzlet és szerviz",
    "ev-06": "Kapcsolat – Trek importőr / Nella",
    "ev-07": "Trek kereskedések Budapesten – trek.hu",
    "ev-08": "Ügyfélszolgálat – K2 Shop",
    "ev-09": "Kapcsolat – BikeArt Center",
    "ev-10": "Boltok – BikeArt webshop",
    "ev-11": "Szerviz – BikeArt Center",
    "ev-12": "BikeArt Center – kezdőlap",
    "ev-13": "Kapcsolat / üzletek – Rekord Bike",
    "ev-14": "Szerviz – Rekord Bike (szervezeti szint)",
    "ev-15": "Üzletünk – VOZZY Bike & Snow",
    "ev-16": "Kapcsolat – JóBringa",
    "ev-17": "Heavy Pedál Kerékpárüzlet & Szerviz",
    "ev-18": "Bikeszaki – kezdőlap",
    "ev-19": "Kapcsolat – Bikeszaki",
    "ev-20": "Üzleteink – Biciklikk",
    "ev-21": "Szerviz – Biciklikk",
    "ev-22": "Peppe Kerékpár szaküzlet és szerviz",
    "ev-23": "Bicó Kerékpárbolt és Kerékpárszerviz",
    "ev-24": "Vitál Club kerékpárbolt – Fehérvár Kerékpár",
    "ev-25": "q1 kerékpárszalon",
    "ev-26": "Melux / Bike Shop Nyíregyháza",
    "ev-27": "Borsod Bike",
    "ev-28": "Rekord Bike – kezdőlap",
}

VARIANT_EV = {
    "ev-cube-kathmandu-one-800": {
        "pageTitle": "Kathmandu Hybrid ONE 800 – CUBE Bikes",
        "variantId": "var-cube-kathmandu-hybrid-one-800-metallicgrey",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "colorAsListed",
            "frameVariant",
        ],
    },
    "ev-giant-explore-eplus-1-stagger": {
        "pageTitle": "Explore E+ 1 Stagger (2026) – Giant",
        "variantId": "var-giant-explore-eplus-1-stagger-2026",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "manufacturerRangeClaim",
            "colorAsListed",
            "frameVariant",
        ],
    },
    "ev-merida-espresso-575-eq": {
        "pageTitle": "eSPRESSO 575 EQ (archived) – MERIDA",
        "variantId": "var-merida-espresso-575-eq-750",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "weighingConditions",
            "colorAsListed",
        ],
    },
    "ev-gepida-berig-deore-10-w": {
        "pageTitle": "BERIG DEORE 10 W – Gepida",
        "variantId": "var-gepida-berig-deore-10-w-500",
        "fields": [
            "exactName",
            "motorExactType",
            "motorPosition",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "manufacturerSku",
            "colorAsListed",
        ],
    },
    "ev-cube-reaction-one-800": {
        "pageTitle": "Reaction Hybrid ONE 800 – CUBE Bikes",
        "variantId": "var-cube-reaction-hybrid-one-800-royalgreen",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "colorAsListed",
            "frameVariant",
        ],
    },
    "ev-merida-ebignine-675": {
        "pageTitle": "eBIG.NINE 675 (archived) – MERIDA",
        "variantId": "var-merida-ebignine-675-750",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "weighingConditions",
            "colorAsListed",
        ],
    },
    "ev-specialized-s-works-levo-4": {
        "pageTitle": "S-Works Turbo Levo 4 – Specialized",
        "variantId": "var-specialized-s-works-turbo-levo-4-840",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "weighingConditions",
            "manufacturerRangeClaim",
            "manufacturerSku",
        ],
    },
    "ev-gepida-sirmium-pro-deore-10": {
        "pageTitle": "SIRMIUM PRO DEORE 10 – Gepida",
        "variantId": "var-gepida-sirmium-pro-deore-10-500",
        "fields": [
            "exactName",
            "motorExactType",
            "motorPosition",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "manufacturerSku",
            "colorAsListed",
        ],
    },
    "ev-specialized-turbo-como-4-0": {
        "pageTitle": "2025 Turbo Como 4.0 – Specialized",
        "variantId": "var-specialized-turbo-como-4-0-710-2025",
        "fields": [
            "exactName",
            "motorExactType",
            "motorPosition",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "manufacturerRangeClaim",
            "manufacturerSku",
            "colorAsListed",
        ],
    },
    "ev-trek-district-plus-9": {
        "pageTitle": "District+ 9 – Trek Bikes",
        "variantId": "var-trek-district-plus-9-powertube-500",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "weighingConditions",
            "manufacturerSku",
            "frameVariant",
        ],
    },
    "ev-cube-supreme-deluxe-one-625": {
        "pageTitle": "Supreme Hybrid Deluxe ONE 625 – CUBE Bikes",
        "variantId": "var-cube-supreme-hybrid-deluxe-one-625-slateblack",
        "fields": [
            "exactName",
            "motorExactType",
            "torqueNm",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "brakes",
            "weightKg",
            "colorAsListed",
            "frameVariant",
        ],
    },
    "ev-gepida-bonum-edge-nexus-8c": {
        "pageTitle": "BONUM EDGE NEXUS 8C (COASTER) – Gepida",
        "variantId": "var-gepida-bonum-edge-nexus-8c-coaster-400",
        "fields": [
            "exactName",
            "motorExactType",
            "motorPosition",
            "batteryWh",
            "batteryExact",
            "drivetrain",
            "manufacturerSku",
            "colorAsListed",
        ],
    },
}

# Extra Trek brand links from trek.hu dealer list (ev-07) where brandClaims empty
EXTRA_TREK_LOCS = {
    "loc-k2-pacsirtamezo": {
        "sourceUrl": "https://trek.hu/hu-hu/Trek_cikkek/Trek_kereskedesek-Budapesten",
        "quote": "Trek kereskedések Budapesten listában (K2 Shop)",
        "evidenceId": "ev-07",
    }
}


def load(name: str):
    with (CONTENT / name).open(encoding="utf-8") as f:
        return json.load(f)


def dump(name: str, data) -> None:
    path = CONTENT / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_brand(name: str):
    key = (name or "").strip().lower()
    return BRAND_NAME_TO_ID.get(key)


def evidence_id_for_url(evidence_items, url: str):
    for e in evidence_items:
        if e.get("url") == url:
            return e["id"]
    return None


def fix_locations(raw_locs, evidence_items):
    ev_by_loc = {}
    for e in evidence_items:
        for s in e.get("supports") or []:
            if isinstance(s, str) and s.startswith("loc-"):
                ev_by_loc.setdefault(s, []).append(e["id"])

    url_to_ev = {e["url"]: e["id"] for e in evidence_items}
    out = load("locations.json")
    by_id = {l["id"]: l for l in out["items"]}
    raw_by_id = {l["id"]: l for l in raw_locs}

    for loc in out["items"]:
        rid = loc["id"]
        raw = raw_by_id.get(rid, {})
        claims = raw.get("brandClaims") or []
        brand_links = []
        external = []
        for c in claims:
            brand_name = c.get("brand")
            bid = resolve_brand(brand_name)
            eid = url_to_ev.get(c.get("sourceUrl")) or (
                (ev_by_loc.get(rid) or [None])[0]
            )
            link = {
                "brandId": bid,
                "brandName": brand_name,
                "relation": c.get("relation") or "sells_brand",
                "sourceUrl": c.get("sourceUrl"),
                "quote": c.get("quote"),
                "evidenceId": eid,
                "disclaimer": DISCLAIMER,
                "inCatalog": bool(bid),
            }
            if bid:
                brand_links.append(link)
            else:
                external.append(link)

        # LOOK pedals-only claim stays external (not bike brand catalog link)
        if rid in EXTRA_TREK_LOCS and not any(b["brandId"] == "brand-trek" for b in brand_links):
            extra = EXTRA_TREK_LOCS[rid]
            brand_links.append(
                {
                    "brandId": "brand-trek",
                    "brandName": "Trek",
                    "relation": "sells_brand",
                    "sourceUrl": extra["sourceUrl"],
                    "quote": extra["quote"],
                    "evidenceId": extra["evidenceId"],
                    "disclaimer": DISCLAIMER,
                    "inCatalog": True,
                }
            )

        loc["brandLinks"] = brand_links
        loc["evidenceIds"] = sorted(set(ev_by_loc.get(rid, [])))
        # Keep editorial notes public; research-only extras separate
        prev_rn = loc.get("researchNotes") or {}
        loc["researchNotes"] = {
            "externalBrandClaims": [
                {
                    "brandName": x["brandName"],
                    "relation": x["relation"],
                    "sourceUrl": x["sourceUrl"],
                    "quote": x["quote"],
                    "evidenceId": x["evidenceId"],
                    "note": "Katalóguson kívüli márka — nincs stabil brandId ebben a próbakörben.",
                }
                for x in external
                if x["brandName"] != "LOOK"
            ],
            "excludedClaims": [
                {
                    "brandName": x["brandName"],
                    "reason": "LOOK pedál-állításként szerepelt; nem kerékpármárka sells_brand.",
                    "sourceUrl": x["sourceUrl"],
                }
                for x in external
                if x["brandName"] == "LOOK"
            ],
        }
        # Preserve audit notes (e.g. stripped szerviz) across brandLinks rebuilds
        for key in ("unverifiedServices",):
            if prev_rn.get(key):
                loc["researchNotes"][key] = prev_rn[key]
        if not loc.get("notes"):
            loc["notes"] = raw.get("notes")

    dump("locations.json", out)
    return by_id


def fix_services():
    doc = load("services.json")
    kept = []
    for s in doc["items"]:
        if s["id"] in ("svc-rekord-bp-szerviz", "svc-rekord-gyor-szerviz"):
            continue
        kept.append(s)
    # Organization-level research note for Rekord szerviz
    doc["items"] = kept
    doc["organizationLevelNotes"] = [
        {
            "organizationId": "org-rekord-bike",
            "topic": "szerviz",
            "status": "előkészített",
            "sourceUrl": "https://rekordbike.hu/szerviz",
            "evidenceId": "ev-14",
            "note": (
                "A Rekord Bike szerviz oldala szervezeti szintű; nem nevezi meg, "
                "hogy Budapesten, Győrben vagy mindkét telephelyen van-e műhely. "
                "Telephelyi szerviz szerep ezért nem publikált."
            ),
        }
    ]
    dump("services.json", doc)


def fix_evidence():
    doc = load("evidence.json")
    for e in doc["items"]:
        eid = e["id"]
        if eid in LOC_EV_TITLES and not e.get("pageTitle"):
            e["pageTitle"] = LOC_EV_TITLES[eid]
        # Normalize supports to list of field/entity refs
        if isinstance(e.get("supports"), str):
            e["supports"] = [e["supports"]]
        if e.get("supports") is None and eid in VARIANT_EV:
            meta = VARIANT_EV[eid]
            e["supports"] = [f"{meta['variantId']}.{f}" for f in meta["fields"]]
            e["pageTitle"] = meta["pageTitle"]
        if eid == "ev-14":
            e["supports"] = ["org-rekord-bike.szerviz-szervezeti"]
            e["status"] = "előkészített"
            e["pageTitle"] = LOC_EV_TITLES["ev-14"]
            e["note"] = (
                "Szerviz oldal org-szinten; telephelyi hozzárendelés nélkül tartva."
            )

    # Replace weak manuals-only explainer sources with concrete Bosch pages
    # Keep manuals, add batteries + range assistant
    existing_ids = {e["id"] for e in doc["items"]}
    extras = [
        {
            "id": "ev-bosch-batteries",
            "url": "https://www.bosch-ebike.com/en/products/batteries",
            "pageTitle": "eBike batteries – Bosch eBike Systems",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-wh.batteryWhDefinition",
                "art-exp-wh.energyContentWh",
                "art-exp-range.batteryInfluenceOnRange",
            ],
            "status": "ellenőrzött",
            "quote": (
                "The eBike battery … has a critical influence on the range. "
                "Energy content listed in Wh (e.g. approx. 400–800 Wh)."
            ),
        },
        {
            "id": "ev-bosch-range-assistant",
            "url": "https://www.bosch-ebike.com/en/service/range-assistant",
            "pageTitle": "Calculate eBike range: How far can you get? | Bosch",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-range.rangeIsEstimate",
                "art-exp-range.influencingFactors",
                "art-exp-wh.rangeVsCapacity",
            ],
            "status": "ellenőrzött",
            "quote": "Official Bosch Range Assistant for estimating eBike range under variable conditions.",
        },
        {
            "id": "ev-bosch-cx-manual-nm",
            "url": "https://help.bosch-ebike.com/hu/connect/help-center/manuals",
            "pageTitle": "Útmutatók – Performance Line CX kézikönyvek listája | Bosch eBike Connect",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-motor.driveUnitTypes",
                "art-exp-nm.torqueUnitNm",
                "art-exp-nm.maxTorqueSpec",
            ],
            "status": "ellenőrzött",
            "quote": (
                "Hivatalos kezelési útmutatók a Performance Line CX és más hajtásegységekhez; "
                "a specifikációk Nm-ben adják meg a maximális nyomatékot."
            ),
        },
        {
            "id": "ev-trek-weight-conditions",
            "url": "https://www.trekbikes.com/gb/en_GB/bikes/hybrid-bikes/electric-hybrid-bikes/district/district-9/p/33186/",
            "pageTitle": "District+ 9 – weight excluding battery | Trek",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-weight.weighingConditionsMatter",
                "var-trek-district-plus-9-powertube-500.weightKg",
                "var-trek-district-plus-9-powertube-500.weighingConditions",
            ],
            "status": "ellenőrzött",
            "quote": "L - 24.90 kg / 54.9 lbs (excluding battery)",
        },
        {
            "id": "ev-specialized-weight-disclaimer",
            "url": "https://www.specialized.com/us/en/s-works-turbo-levo-4/p/4291509",
            "pageTitle": "S-Works Turbo Levo 4 – weight conditions | Specialized",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-weight.weighingConditionsMatter",
                "var-specialized-s-works-turbo-levo-4-840.weightKg",
                "var-specialized-s-works-turbo-levo-4-840.weighingConditions",
            ],
            "status": "ellenőrzött",
            "quote": (
                "Weight Size S4; weights based on production painted frames as pictured; "
                "actual weights vary by colorway, frame size, and component variation"
            ),
        },
        {
            "id": "ev-bikeart-szerviz",
            "url": "https://www.bikeart.hu/szerviz.html",
            "pageTitle": "Szerviz – BikeArt Center",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-service.localServiceCapacity",
                "svc-bikeart-csalogany-szerviz",
                "svc-bikeart-kissjanos-szerviz",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-biciklikk-ebike-szerviz",
            "url": "https://www.biciklikk.hu/szerviz",
            "pageTitle": "Szerviz – Biciklikk (e-bike javítás)",
            "accessedAt": ACCESS,
            "supports": [
                "art-exp-service.ebikeServiceDistinct",
                "svc-biciklikk-szerviz",
                "svc-biciklikk-ebike",
            ],
            "status": "ellenőrzött",
            "quote": "elektromos kerékpárok (e-bike, pedelec) javítása; rendszerdiagnosztika",
        },
    ]
    for ex in extras:
        if ex["id"] not in existing_ids:
            doc["items"].append(ex)
        else:
            for i, e in enumerate(doc["items"]):
                if e["id"] == ex["id"]:
                    doc["items"][i] = ex
                    break

    # Fix bosch help supports to arrays
    for e in doc["items"]:
        if e["id"] == "ev-bosch-help-manuals":
            e["supports"] = [
                "art-exp-motor.manualsAvailable",
                "art-exp-nm.manualsAvailable",
            ]
        if e["id"] == "ev-bosch-help-range-nyon":
            e["supports"] = [
                "art-exp-range.displayEstimate",
                "art-exp-wh.displayEstimate",
            ]

    dump("evidence.json", doc)
    return {e["id"]: e for e in doc["items"]}


def fix_variants():
    doc = load("variants.json")
    conflicts = doc.get("conflicts") or []
    conflict_fields = {}
    archived = set()
    for c in conflicts:
        vids = c.get("variantIds") or ([c["variantId"]] if c.get("variantId") else [])
        if c.get("id") == "conflict-merida-archived-status":
            archived.update(vids)
        for vid in vids:
            conflict_fields.setdefault(vid, set()).update(c.get("fields") or [])

    ev_for_var = {m["variantId"]: eid for eid, m in VARIANT_EV.items()}

    for v in doc["items"]:
        vid = v["id"]
        eid = ev_for_var.get(vid)
        v["evidenceIds"] = [eid] if eid else []
        flags = []
        if vid in archived:
            flags.append("archivált")
            v["status"] = "előkészített"
            v["archiveNote"] = (
                "Hivatalos gyártói oldal archived jelölésű; a specifikáció olvasható, "
                "de aktuális gyártási státusz nem igazolt."
            )
        cf = sorted(conflict_fields.get(vid) or [])
        # Map conflict field names to variant keys
        unresolved = []
        for f in cf:
            if f in ("drivetrain", "brakes", "colorAsListed", "tires"):
                unresolved.append(f)
            elif f.startswith("motor"):
                unresolved.append("motorExactType")
        if unresolved:
            flags.append("ellentmondás")
            v["unresolvedFields"] = sorted(set(unresolved))
            # Soften conflict display values
            if "brakes" in unresolved and v.get("brakes"):
                v["brakesDisplay"] = (
                    "A forrásban kontrafék és tárcsafék is szerepel — "
                    "a féktípust ezért nem közöljük ellenőrzött adatként."
                )
            if "drivetrain" in unresolved:
                v["drivetrainNote"] = (
                    "A marketing egyes modelleknél öves hajtást is említ; "
                    "ennél a változatnál a Specs Shimano Cues Di2 váltós hajtást listáz. "
                    "Itt a Specs szerinti adat szerepel."
                )
            if "colorAsListed" in unresolved:
                v["colorAsListed"] = (
                    "Ellentmondás a forrásban: cím/URL matt grafit, specifikáció matrica szín MENTA"
                )
        missing = []
        for field, reason_key in [
            ("torqueNm", "torqueNote"),
            ("weightKg", "weightMissingReason"),
            ("motorPosition", "motorPositionMissingReason"),
            ("weighingConditions", "weighingConditionsMissingReason"),
        ]:
            if v.get(field) is None:
                missing.append(field)
        if missing:
            flags.append("hiányzó_adat")
            v["missingFields"] = missing
        v["dataFlags"] = flags
        # Editorial: expand Trek weighing display
        if vid == "var-trek-district-plus-9-powertube-500":
            v["weightDisplay"] = "24,9 kg, akkumulátor nélkül"
            v["weighingConditions"] = (
                "L méret: 24,90 kg / 54,9 lbs, akkumulátor nélkül; "
                "előgyártási festett vázakon alapuló adat a közzététel idején; "
                "a végleges gyártásban eltérhet."
            )
        # Fix awkward characters in color names
        if isinstance(v.get("colorAsListed"), str):
            v["colorAsListed"] = (
                v["colorAsListed"]
                .replace("´n´", " n ")
                .replace("´", "'")
            )

    # Rename comparison group
    for g in doc.get("comparisonGroups") or []:
        if g["id"] == "cmp-compact-urban":
            g["id"] = "cmp-city-comfort"
            g["useCase"] = "city-comfort-everyday"
            g["title"] = "Városi / mindennapi komfort e-bike"
            g["slug"] = "osszehasonlitas-varosi-komfort-e-bike"
        if g["id"] == "cmp-e-mtb":
            g["title"] = "E-MTB: hardtail és összteleszkópos"
            g["note"] = (
                "A hardtail csak elöl rugóz; az összteleszkópos elöl és hátul is. "
                "A felépítés eltérése nem rangsor."
            )
        if g["id"] == "cmp-city-trekking":
            g["title"] = "Városi / trekking e-bike"

    # Update conflict id reference for renamed group is N/A
    dump("variants.json", doc)


def fix_products():
    doc = load("products.json")
    for p in doc["items"]:
        note = (p.get("pageNote") or "").lower()
        if "archived" in note:
            p["status"] = "előkészített"
            p["dataFlags"] = ["archivált"]
        else:
            p.setdefault("dataFlags", [])
            if p.get("status") == "ellenőrzött" and not p.get("dataFlags"):
                p["dataFlags"] = []
    dump("products.json", doc)


def fmt_val(v):
    if v is None or v == "":
        return NA
    return str(v)


def build_pros_cons():
    """Visitor-facing bullets. Keys pros/cons kept for schema; headings change in markdown."""
    return {
        "var-cube-kathmandu-hybrid-one-800-metallicgrey": {
            "pros": [
                "800 Wh akkumulátor és Bosch Performance Line CX (BDU38), max. 120 Nm — a csoport magasabb gyártói energia- és nyomatékértékei között.",
                "Hidraulikus tárcsafék (180/180 mm) és 10 fokozatú Cues hajtás: túrázáshoz és mindennapi használathoz illő felszereltség a katalógus szerint.",
            ],
            "cons": [
                "Gyártói tömeg 28,4 kg, méret és felszereltség megadása nélkül — a szám csak tájékoztató.",
                "A motor elhelyezését (közép-/agy motor) a gyártói oldalon nem címkézték külön.",
            ],
        },
        "var-giant-explore-eplus-1-stagger-2026": {
            "pros": [
                "800 Wh EnergyPak és SyncDrive Pro2, 85 Nm; a gyártó három kategóriás hatótáv-becslést is közöl (nem mért teszt).",
                "4 dugattyús Deore hidraulikus tárcsafék (203/180 mm) — a csoport erősebb fékkínálata között.",
            ],
            "cons": [
                "Ehhez a változathoz nincs ellenőrzött tömegadatunk; a gyártó helyi mérést javasol.",
                "A marketing egyes modelleknél öves hajtást is említ; ennél a változatnál a Specs Di2 váltós hajtást listáz — a táblában ez utóbbi szerepel.",
            ],
        },
        "var-merida-espresso-575-eq-750": {
            "pros": [
                "750 Wh belső akkumulátor és Shimano EP6, 85 Nm; tömeg 27,1 kg, M vázméreten mérve.",
                "EQ felszereltségű trekking jelleg a gyártói specifikáció alapján.",
            ],
            "cons": [
                "Archivált gyártói oldal: a specifikáció olvasható; azt, hogy jelenleg is gyártják, nem igazoltuk.",
                "A modellév a gyártói oldalon nem szerepel külön számként.",
            ],
        },
        "var-gepida-berig-deore-10-w-500": {
            "pros": [
                "Középmotoros Bosch Performance Line Cruise BES2 és 500 Wh; a gyártó SUV jellegű használatra pozicionálja.",
                "Deore 10 fokozatú hajtás és hidraulikus tárcsafék a specifikációban.",
            ],
            "cons": [
                "A nyomatékhoz (Nm) és a tömeghez nincs ellenőrzött adatunk a gepida.hu oldalon.",
                "A színmegnevezés a forráson belül ellentmondásos (cím vs. matrica szín).",
            ],
        },
        "var-cube-reaction-hybrid-one-800-royalgreen": {
            "pros": [
                "Merevvázas (hardtail) e-MTB: 800 Wh és Bosch CX max. 120 Nm (BDU38) — magas gyártói energia- és nyomatékérték.",
                "Gyártói tömeg 25,9 kg; mérési feltétel nélkül, ezért nem alkalmas rangsoroláshoz.",
            ],
            "cons": [
                "Csak első teleszkóp van: technikás ösvényen más a karakter, mint az összteleszkópos modelleknél.",
                "A tömeghez nincs megadva méret vagy felszereltség.",
            ],
        },
        "var-merida-ebignine-675-750": {
            "pros": [
                "Merevvázas e-MTB 750 Wh-vel és Shimano EP6 85 Nm-rel; tömeg 23,6 kg M méreten (feltétel megadva).",
                "12 fokozatú Eagle hajtás a specifikáció szerint.",
            ],
            "cons": [
                "Archivált gyártói oldal: a specifikáció olvasható; azt, hogy jelenleg is gyártják, nem igazoltuk.",
                "Nincs hátsó teleszkóp: ez szándékos felépítés (egyszerűbb hátsó rész, más terepes karakter).",
            ],
        },
        "var-specialized-s-works-turbo-levo-4-840": {
            "pros": [
                "Összteleszkópos e-MTB, 150 mm hátsó rugóúttal: elöl és hátul rugóz — más felépítés, mint a merevvázas modelleké.",
                "840 Wh akkumulátor, 111 Nm / 850 W gyártói motoradat; tömeg 23,68 kg S4 méreten, feltétellel.",
            ],
            "cons": [
                "S-Works szintű felszereltség: prémium hajtás és fék a listán — nem „jobb hardtail”, hanem más kategória.",
                "A hatótáv-közlés Eco módra és Range Extender feltételekre épül — nem független mérés.",
            ],
        },
        "var-gepida-sirmium-pro-deore-10-500": {
            "pros": [
                "Merevvázas e-MTB középmotoros Bosch Performance Line CX BES2 motorral (85 Nm) és 500 Wh akkumulátorral.",
                "Deore 10 fokozat és hidraulikus tárcsafék a specifikáció táblájában.",
            ],
            "cons": [
                "Ehhez a változathoz nincs ellenőrzött tömegadatunk; a gumi megnevezése a marketing és a Specs között eltér.",
                "500 Wh a csoport kisebb gyártói kapacitása a 750–840 Wh modellekhez képest — ez kapacitáskülönbség, nem rangsor.",
            ],
        },
        "var-specialized-turbo-como-4-0-710-2025": {
            "pros": [
                "Átlépős városi váz; 710 Wh U2 akkumulátor és Specialized 2.0 motor, 70 Nm — a csoport magasabb Wh-értékei között.",
                "A gyártó Eco módban hatótáv-közlést is feltüntet (nem független mérés).",
            ],
            "cons": [
                "Ehhez a változathoz nincs ellenőrzött tömegadatunk.",
                "Nem összecsukható modell: mindennapi városi komfortbringa.",
            ],
        },
        "var-trek-district-plus-9-powertube-500": {
            "pros": [
                "Tömeg: 24,9 kg, akkumulátor nélkül, L-es vázméretben — a feltétel a gyártói oldalon szerepel.",
                "Enviolo fokozatmentes váltó és Gates szíjhajtás: kevesebb lánckarbantartást igénylő városi hajtás a specifikáció szerint.",
            ],
            "cons": [
                "500 Wh PowerTube — kisebb gyártói energiatartalék, mint a 625–710 Wh társaknál.",
                "65 Nm Bosch Performance; a motor elhelyezését a gyártói oldalon nem címkézték külön.",
            ],
        },
        "var-cube-supreme-hybrid-deluxe-one-625-slateblack": {
            "pros": [
                "Könnyű beszállású váz, Nexus 8 agyváltó és Gates szíj: mindennapi városi komfortfelszereltség.",
                "625 Wh PowerTube; Active Line Plus, 50 Nm a gyártói adat szerint.",
            ],
            "cons": [
                "Gyártói tömeg 27,8 kg, mérési feltétel nélkül.",
                "50 Nm a csoport alacsonyabb nyomatékértéke: sík városi használatra tipikus, emelkedőn más a karakter.",
            ],
        },
        "var-gepida-bonum-edge-nexus-8c-coaster-400": {
            "pros": [
                "Vázba integrált 400 Wh és középmotoros Active Line Plus BES2; Nexus 8 agyváltó városi használathoz.",
                "A csoport kisebb Wh-értéke: kisebb energiatartalék a gyártói adat szerint.",
            ],
            "cons": [
                "A nyomatékhoz és a tömeghez nincs ellenőrzött adatunk a gepida.hu oldalon.",
                "A forrásban kontrafék és tárcsafék is szerepel — a féktípust ezért nem közöljük ellenőrzött adatként.",
            ],
        },
    }


def write_md(slug: str, body: str) -> None:
    (CONTENT / "articles" / f"{slug}.md").write_text(body.strip() + "\n", encoding="utf-8")


def fix_articles():
    variants = {v["id"]: v for v in load("variants.json")["items"]}
    pc = build_pros_cons()

    explainers = [
        {
            "id": "art-exp-motor",
            "type": "magyarazo",
            "title": "Mit jelent az e-bike motor?",
            "slug": "e-bike-motor-magyarazo",
            "status": "ellenőrzött",
            "relatedBrandIds": [],
            "relatedVariantIds": [],
            "evidenceIds": ["ev-bosch-cx-manual-nm", "ev-bosch-help-manuals"],
            "checkedAt": ACCESS,
            "bodyMarkdown": """## Mit jelent?

Az elektromos rásegítésű kerékpár (pedelec) motorja a pedálozáshoz ad plusz erőt. Gyártói adatlapokon a pontos típusjelzés az elsődleges azonosító — például Bosch Performance Line CX, Shimano EP6 vagy Specialized saját egység —, nem elég csak a márkanevet nézni.

A Bosch eBike hivatalos dokumentációja külön kezelési útmutatókat közöl a különböző hajtásegységekhez (Active Line, Performance Line CX stb.).

## Miért számít használat közben?

A motor karakterisztikája befolyásolja az indulást, az emelkedőt és azt, mennyire természetesnek hat a rásegítés. A motor önmagában nem határozza meg a kerékpárt: a váz, a váltó, a gumi és a tömeg ugyanúgy számít.

## Mivel együtt értelmezd?

- Nyomaték (Nm) és maximális rásegítési szint
- Akkumulátor kapacitása (Wh) és a választott menetmód
- Váltó és áttétel
- A kerékpár össztömege

## Mit ellenőrizz vásárláskor?

1. A pontos motortípust a gyártói oldalon vagy a típustáblán.
2. Hogy a szerviz ismeri-e az adott rendszert (általános e-bike-szerviz nem egyenlő automatikus márka- vagy rendszerszervizzel).
3. A szoftver- és kijelző-kompatibilitást, ha a gyártó említi.

## Gyakori félreértés

„Erősebb motor = jobb bringa.” A nagyobb nyomatékú vagy sportosabb motor más karaktert ad, de nem jelenti automatikusan, hogy minden használatra jobb — és több energiát is fogyaszthat.

## Források

- Bosch eBike Connect – hivatalos kezelési útmutatók: https://help.bosch-ebike.com/hu/connect/help-center/manuals
""",
        },
        {
            "id": "art-exp-nm",
            "type": "magyarazo",
            "title": "Mit jelent a nyomaték (Nm) e-bike-nál?",
            "slug": "e-bike-nyomatek-nm-magyarazo",
            "status": "ellenőrzött",
            "relatedBrandIds": [],
            "relatedVariantIds": [],
            "evidenceIds": ["ev-bosch-cx-manual-nm", "ev-bosch-help-manuals"],
            "checkedAt": ACCESS,
            "bodyMarkdown": """## Mit jelent?

A newtonméter (Nm) a motor forgatónyomatékának mértékegysége a gyártói specifikációban. Azt jelzi, mekkora csavaró erőt képes a hajtás leadni — tipikusan maximális értékként feltüntetve. A Bosch hajtásegység-útmutatók a maximális nyomatékot Nm-ben adják meg.

## Miért számít használat közben?

Emelkedőn, induláskor vagy nagyobb terhelésnél a nagyobb nyomaték gyakran könnyebb rásegítést ad. Síkon, alacsony rásegítéssel a különbség kevésbé érezhető. A menetérzetet a vezérlés, a szenzorok és az áttétel is alakítja.

## Mivel együtt értelmezd?

- Motortípus és rásegítési módok
- Akkumulátor (Wh) — erősebb rásegítés gyorsabban meríthet
- Kerékpár és rakomány tömege
- Guminyomás és terep

## Mit ellenőrizz vásárláskor?

1. A gyártó által megadott Nm értéket a konkrét modellváltozathoz.
2. Hogy milyen maximális sebességig ad rásegítést a rendszer (pedelec keretek).
3. Különböző generációjú motorok Nm számait ne hasonlítsd össze kontextus nélkül.

## Gyakori félreértés

„A nagyobb Nm mindig jobb.” Magasabb Nm nem automatikus győztes: fogyasztás, karakter és a teljes felszereltség együtt dönt.

## Források

- Bosch eBike Connect – kezelési útmutatók (hajtásegységek, Nm): https://help.bosch-ebike.com/hu/connect/help-center/manuals
""",
        },
        {
            "id": "art-exp-wh",
            "type": "magyarazo",
            "title": "Mit jelent az akkukapacitás (Wh)?",
            "slug": "e-bike-akkukapacitas-wh-magyarazo",
            "status": "ellenőrzött",
            "relatedBrandIds": [],
            "relatedVariantIds": [],
            "evidenceIds": ["ev-bosch-batteries", "ev-bosch-range-assistant"],
            "checkedAt": ACCESS,
            "bodyMarkdown": """## Mit jelent?

A wattóra (Wh) az akkumulátorban tárolható energia mennyiségét jelzi. A Bosch eBike Systems akkumulátor-oldala az energiatartalmat Wh-ben adja meg (például PowerTube / PowerPack sorozatok kb. 360–800 Wh tartományban), és kiemeli: az akku kritikusan befolyásolja a hatótávot.

## Miért számít használat közben?

Több Wh általában nagyobb tartalékot ad hosszú útra vagy magasabb rásegítéshez. A tényleges megtett kilométer ettől még sok tényezőtől függ.

## Mivel együtt értelmezd?

- Rásegítési mód
- Terep, szél, hőmérséklet
- Össztömeg (bringás + csomag)
- Motor hatékonysága és sebesség

## Mit ellenőrizz vásárláskor?

1. A pontos Wh értéket és az akku típusát a modellváltozathoz.
2. Cserélhető-e / levehető-e az akku, és hol tölthető.
3. A gyártó hatótáv-közlését becslésként kezeld; nézd a feltételeket, ha megadják.

## Gyakori félreértés

„750 Wh mindig messzebb visz, mint 500 Wh.” Nagyobb kapacitás több energiát tárol, de agresszív rásegítéssel vagy meredek terepen a különbség nem arányos automatikusan a Wh-aránnyal.

## Források

- Bosch eBike Systems – akkumulátorok (Wh / energiatartalom): https://www.bosch-ebike.com/en/products/batteries
- Bosch Range Assistant: https://www.bosch-ebike.com/en/service/range-assistant
""",
        },
        {
            "id": "art-exp-range",
            "type": "magyarazo",
            "title": "Mit jelent az e-bike hatótáv?",
            "slug": "e-bike-hatotav-magyarazo",
            "status": "ellenőrzött",
            "relatedBrandIds": [],
            "relatedVariantIds": [],
            "evidenceIds": ["ev-bosch-range-assistant", "ev-bosch-batteries", "ev-bosch-help-range-nyon"],
            "checkedAt": ACCESS,
            "bodyMarkdown": """## Mit jelent?

A hatótáv az a távolságbecslés, amit egy töltéssel várhatsz. A Bosch hivatalos Range Assistant oldala kifejezetten a változó feltételek melletti becslésre szolgál — a kijelzőn vagy kalkulátorban megjelenő szám jellemzően becslés, nem minden körülményre garantált mért eredmény.

## Miért számít használat közben?

Segít tervezni a túrát és a töltési pontokat. A valós út eltérhet, ha változik a rásegítés, a terep vagy a terhelés.

## Mivel együtt értelmezd?

- Akkukapacitás (Wh)
- Menetmód / rásegítés erőssége
- Sebesség, emelkedők, szél
- Guminyomás, hőmérséklet
- Össztömeg

## Mit ellenőrizz vásárláskor?

1. A gyártói hatótáv-szám mellett a feltételeket (ha közlik).
2. Hogy a bolt tud-e demót / kipróbálást — ezt külön kell igazolni.
3. Saját tipikus útvonaladon milyen rásegítést használnál.

## Gyakori félreértés

„A katalógusban szereplő km a te utadra is igaz.” A katalógusérték más körülmények között készülhet; a kijelző becslése is változhat menet közben.

## Források

- Bosch Range Assistant: https://www.bosch-ebike.com/en/service/range-assistant
- Bosch akkumulátorok (hatótávra gyakorolt hatás): https://www.bosch-ebike.com/en/products/batteries
- Bosch eBike Connect – hatótáv a Nyon kijelzőn: https://help.bosch-ebike.com/hu/connect/help-center/ebc-nyonbui350-firststeps/asset-asf-00098
""",
        },
        {
            "id": "art-exp-weight",
            "type": "magyarazo",
            "title": "Mit jelent az e-bike tömege?",
            "slug": "e-bike-tomeg-magyarazo",
            "status": "ellenőrzött",
            "relatedBrandIds": [],
            "relatedVariantIds": ["var-trek-district-plus-9-powertube-500"],
            "evidenceIds": ["ev-trek-weight-conditions", "ev-specialized-weight-disclaimer"],
            "checkedAt": ACCESS,
            "bodyMarkdown": """## Mit jelent?

A gyártói tömeg (kg) a kerékpár súlyát jelöli. Fontos, hogy milyen felszereltséggel és melyik vázméretre vonatkozik. Példa: a Trek District+ 9 oldalán a tömeg **24,9 kg, akkumulátor nélkül, L-es vázméretben** — a feltétel a számmal együtt szerepel. A Specialized termékoldalak gyakran méretre és festett gyártási vázakra hivatkoznak, és jelzik, hogy a szín, méret és alkatrészváltozat módosíthatja az értéket.

## Miért számít használat közben?

Nehezebb bringát emelni, szállítani, lépcsőzni nehezebb; a kezelhetőség és a rásegítés nélküli pedálozás is más lehet.

## Mivel együtt értelmezd?

- Akkumulátor tömege / elhelyezése (akkuval vagy anélkül mérték-e)
- Teherhordó felszerelés
- Maximális megengedett össztömeg (ha a gyártó megadja)
- A te testtömeged és a tipikus csomag

## Mit ellenőrizz vásárláskor?

1. Van-e megadva a mérési feltétel (méret, akkuval / akkumulátor nélkül)?
2. Ha nincs feltétel: a kg értéket tájékoztatónak tekintsd.
3. Ne rangsorolj abszolút győztest kis kg-különbségből, ha a feltételek hiányoznak vagy eltérnek.

## Gyakori félreértés

„A könnyebb mindig jobb.” Városi teherhordásra tervezett modelleknél a nagyobb tömeg kompromisszum lehet, nem feltétlenül hiba.

## Források

- Trek District+ 9 – tömeg akkumulátor nélkül: https://www.trekbikes.com/gb/en_GB/bikes/hybrid-bikes/electric-hybrid-bikes/district/district-9/p/33186/
- Specialized S-Works Turbo Levo 4 – tömegfeltételek: https://www.specialized.com/us/en/s-works-turbo-levo-4/p/4291509
""",
        },
        {
            "id": "art-exp-service",
            "type": "magyarazo",
            "title": "Mit jelent az e-bike szervizháttér?",
            "slug": "e-bike-szervizhatter-magyarazo",
            "status": "ellenőrzött",
            "relatedBrandIds": [],
            "relatedVariantIds": [],
            "evidenceIds": ["ev-bikeart-szerviz", "ev-biciklikk-ebike-szerviz", "ev-03"],
            "checkedAt": ACCESS,
            "bodyMarkdown": """## Mit jelent?

A szervizháttér az a helyi kapacitás, ahol a kerékpárt és az elektromos rendszert karbantartják, diagnosztizálják, javítják. Ez lehet általános kerékpárszerviz, e-bike-ra felkészült műhely, vagy igazolt márka-/rendszerszerviz — ezek külön állítások.

Példák ellenőrzött forrásokból: a BikeArt Center külön szervizoldalt közöl; a Biciklikk szervizoldala említi az elektromos kerékpárok (e-bike, pedelec) javítását és a rendszerdiagnosztikát; a Futurebike/Gepida Store elektronikai szervizénél Bosch és TQ rendszerek szerepelnek.

## Miért számít használat közben?

Szoftverfrissítés, hibakód, akku, motorcsatlakozók — ezekhez gyakran speciális eszköz vagy képzés kell.

## Mivel együtt értelmezd?

- A motor/akkumulátor rendszere
- A bolt „márkát árul” állítása nem egyenlő automatikus hivatalos márkaszervizzel
- Telephelyi bizonyíték nélkül szervezeti szervizoldal nem rendelhető automatikusan minden bolthoz

## Mit ellenőrizz vásárláskor?

1. Kérdezd meg: mely rendszereket szervizelnek, milyen diagnosztikával.
2. Különböztetve: eladás / általános szerviz / e-bike-szerviz / igazolt jogosultság.
3. Hol van a legközelebbi, számodra elfogadható távolságú pont.

## Gyakori félreértés

„Ha ott vettem, ott mindent meg is javítanak hivatalosan.” Az eladóhely és az igazolt rendszerszerviz külön állítások.

## Források

- BikeArt szerviz: https://www.bikeart.hu/szerviz.html
- Biciklikk szerviz: https://www.biciklikk.hu/szerviz
- Futurebike kerékpár szerviz: https://www.gepidastore.hu/kerekpar-szerviz/
""",
        },
    ]

    def row_weight(v):
        if v["id"] == "var-trek-district-plus-9-powertube-500":
            return "24,9 kg, akkumulátor nélkül, L-es vázméretben"
        if v.get("weightKg") is None:
            return "Ehhez a változathoz nincs ellenőrzött tömegadatunk."
        cond = v.get("weighingConditions")
        if cond:
            return f"{v['weightKg']} ({cond})"
        return f"{v['weightKg']} (mérési feltétel nélkül)"

    def row_motor(v):
        m = v.get("motorExactType") or NA
        # avoid truncated display in tables
        return m.replace("|", "/")

    def row_nm(v):
        return fmt_val(v.get("torqueNm"))

    def row_brake(v):
        if v.get("brakesDisplay"):
            return v["brakesDisplay"]
        return v.get("brakes") or NA

    def table_md(vids):
        lines = [
            "| Modell | Típus | Motor | Nm | Wh | Tömeg | Forrás |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for vid in vids:
            v = variants[vid]
            lines.append(
                "| {name} | {typ} | {motor} | {nm} | {wh} | {w} | {url} |".format(
                    name=v["exactName"],
                    typ=v.get("bikeType") or NA,
                    motor=row_motor(v),
                    nm=row_nm(v),
                    wh=fmt_val(v.get("batteryWh")),
                    w=row_weight(v),
                    url=v.get("sourceUrl") or NA,
                )
            )
        return "\n".join(lines)

    def pros_cons_md(vids):
        parts = []
        for vid in vids:
            v = variants[vid]
            block = pc[vid]
            parts.append(f"### {v['exactName']}")
            if "archivált" in (v.get("dataFlags") or []):
                parts.append(
                    "*Archivált gyártói oldal: a specifikáció olvasható; azt, hogy jelenleg is gyártják, nem igazoltuk.*"
                )
            parts.append("**Mit érdemes tudnod róla?**")
            for p in block["pros"]:
                parts.append(f"- {p}")
            parts.append("**Mire figyelj vásárlás előtt?**")
            for c in block["cons"]:
                parts.append(f"- {c}")
            parts.append("")
        return "\n".join(parts)

    def table_json(vids):
        rows = []
        for vid in vids:
            v = variants[vid]
            weight_display = row_weight(v)
            rows.append(
                {
                    "variantId": vid,
                    "name": v["exactName"],
                    "trim": v.get("trimOrBatteryVariant"),
                    "bikeType": v.get("bikeType"),
                    "motor": v.get("motorExactType"),
                    "torqueNm": v.get("torqueNm"),
                    "batteryWh": v.get("batteryWh"),
                    "batteryExact": v.get("batteryExact"),
                    "drivetrain": v.get("drivetrain"),
                    "brakes": row_brake(v),
                    "weightKg": v.get("weightKg"),
                    "weightDisplay": weight_display,
                    "weighingConditions": v.get("weighingConditions"),
                    "sourceUrl": v.get("sourceUrl"),
                    "status": v.get("status"),
                    "dataFlags": v.get("dataFlags") or [],
                    "pros": pc[vid]["pros"],
                    "cons": pc[vid]["cons"],
                }
            )
        return rows

    city_ids = [
        "var-cube-kathmandu-hybrid-one-800-metallicgrey",
        "var-giant-explore-eplus-1-stagger-2026",
        "var-merida-espresso-575-eq-750",
        "var-gepida-berig-deore-10-w-500",
    ]
    emtb_ids = [
        "var-cube-reaction-hybrid-one-800-royalgreen",
        "var-merida-ebignine-675-750",
        "var-specialized-s-works-turbo-levo-4-840",
        "var-gepida-sirmium-pro-deore-10-500",
    ]
    comfort_ids = [
        "var-specialized-turbo-como-4-0-710-2025",
        "var-trek-district-plus-9-powertube-500",
        "var-cube-supreme-hybrid-deluxe-one-625-slateblack",
        "var-gepida-bonum-edge-nexus-8c-coaster-400",
    ]

    cmp_city = f"""## Miről szól ez az összehasonlítás?

Mindennapi és túrázós használatra szánt trekking és SUV jellegű e-bike modellváltozatok gyártói adatai. Nem saját teszt, és nincs abszolút győztes.

## Gyártói adatok ({ACCESS})

{table_md(city_ids)}

Ahol „{NA}” vagy hiányzó tömeg szerepel: a rendelkezésre álló gyártói oldalon nem ellenőrzött szám, vagy hiányzik a mérési feltétel.

## Modellenként

{pros_cons_md(city_ids)}

## Hogyan olvasd a különbségeket?

- **Nm és Wh együtt:** nagyobb nyomaték és magasabb rásegítés gyorsabban merítheti az akkumulátort. A Wh önmagában nem hatótávgarancia.
- **Tömeg:** ha nincs mérési feltétel (méret, akkumulátorral vagy anélkül), a kg csak tájékoztató.
- **Motortípus:** a „Bosch CX” felirat különböző generációknál más Nm-értéket jelenthet.
- **Nem saját teszt:** menetélményt, mért hatótávot és abszolút győztest nem állítunk.

## Kinek lehet hasznos?

Ha aszfaltos vagy vegyes útvonalon, csomaggal vagy hosszabb távon is gondolkodsz, és a katalógusadatokból szeretnél kiindulni. Kipróbálást csak akkor tekintsd adottnak, ha a konkrét üzlet ezt állítja.
"""

    cmp_emtb = f"""## Miről szól ez az összehasonlítás?

Terepes használatra szánt e-MTB modellváltozatok. A **S-Works Turbo Levo 4 összteleszkópos** (elöl és hátul rugóz). A CUBE Reaction, a MERIDA eBIG.NINE és a Gepida SIRMIUM **merevvázas (hardtail)**: csak elöl van teleszkóp, a hátsó háromszög merev. Ez felépítésbeli különbség, nem rangsor. Nem saját teszt, és nincs abszolút győztes.

## Merevvázas vagy összteleszkópos?

- **Merevvázas (hardtail):** egyszerűbb hátsó rész, tipikusan könnyebb karbantartás. Technikás, gyökeres vagy köves ösvényen a hátsó kerék kevésbé nyeli az ütést.
- **Összteleszkópos:** hátsó rugóút is van (itt: 150 mm a Levo 4 specifikáció szerint). Más terepes karakter — nem „jobb hardtail”, hanem más konstrukció.

## Gyártói adatok ({ACCESS})

{table_md(emtb_ids)}

Ahol „{NA}” vagy hiányzó tömeg szerepel: a rendelkezésre álló gyártói oldalon nem ellenőrzött szám, vagy hiányzik a mérési feltétel.

## Modellenként

{pros_cons_md(emtb_ids)}

## Hogyan olvasd a különbségeket?

- Merevvázas és összteleszkópos modelleket ne rangsorolj ugyanazon skálán.
- Az Nm és a Wh együtt értelmezendő; a Wh nem hatótávgarancia.
- A MERIDA oldal archivált: a specifikáció olvasható; azt, hogy jelenleg is gyártják, nem igazoltuk.
- Nem saját teszt; abszolút győztes nincs.
"""

    cmp_comfort = f"""## Miről szól ez az összehasonlítás?

Városi, mindennapi közlekedésre szánt komfort e-bike modellváltozatok: átlépős vagy könnyű beszállású váz, agyváltós vagy szíjhajtásos jellegű felszereltség. **Nem** összecsukható „kompakt” kategória. Nem saját teszt, és nincs abszolút győztes.

## Gyártói adatok ({ACCESS})

{table_md(comfort_ids)}

A Trek District+ 9 tömege: **24,9 kg, akkumulátor nélkül, L-es vázméretben** (gyártói feltétel). Ahol hiányzó tömeg vagy „{NA}” szerepel: a rendelkezésre álló oldalon nincs ellenőrzött szám vagy feltétel.

## Modellenként

{pros_cons_md(comfort_ids)}

## Hogyan olvasd a különbségeket?

- A nagyobb Wh nem automatikus győzelem városi használatban.
- Tömegnél a mérési feltétel (akkumulátorral vagy anélkül, méret) legalább annyira számít, mint a szám.
- A Gepida BONUM féktípusa a forráson belül ellentmondásos — fékadatot nem közlünk ellenőrzött tényként.
- Nem saját teszt; abszolút győztes nincs.
"""

    # Remove old compact md if renaming
    old = CONTENT / "articles" / "osszehasonlitas-kompakt-varosi-e-bike.md"
    new_slug = "osszehasonlitas-varosi-komfort-e-bike"
    if old.exists():
        old.unlink()

    comparisons = [
        {
            "id": "art-cmp-city-trekking",
            "type": "osszehasonlitas",
            "title": "Városi / trekking e-bike összehasonlítás",
            "slug": "osszehasonlitas-varosi-trekking-e-bike",
            "status": "ellenőrzött",
            "comparisonGroupId": "cmp-city-trekking",
            "relatedVariantIds": city_ids,
            "relatedBrandIds": [],
            "evidenceIds": [
                "ev-cube-kathmandu-one-800",
                "ev-giant-explore-eplus-1-stagger",
                "ev-merida-espresso-575-eq",
                "ev-gepida-berig-deore-10-w",
            ],
            "checkedAt": ACCESS,
            "table": table_json(city_ids),
            "bodyMarkdown": cmp_city,
        },
        {
            "id": "art-cmp-e-mtb",
            "type": "osszehasonlitas",
            "title": "E-MTB: hardtail és összteleszkópos összehasonlítás",
            "slug": "osszehasonlitas-e-mtb",
            "status": "ellenőrzött",
            "comparisonGroupId": "cmp-e-mtb",
            "relatedVariantIds": emtb_ids,
            "relatedBrandIds": [],
            "evidenceIds": [
                "ev-cube-reaction-one-800",
                "ev-merida-ebignine-675",
                "ev-specialized-s-works-levo-4",
                "ev-gepida-sirmium-pro-deore-10",
            ],
            "checkedAt": ACCESS,
            "table": table_json(emtb_ids),
            "bodyMarkdown": cmp_emtb,
        },
        {
            "id": "art-cmp-city-comfort",
            "type": "osszehasonlitas",
            "title": "Városi / mindennapi komfort e-bike összehasonlítás",
            "slug": new_slug,
            "status": "ellenőrzött",
            "comparisonGroupId": "cmp-city-comfort",
            "relatedVariantIds": comfort_ids,
            "relatedBrandIds": [],
            "evidenceIds": [
                "ev-specialized-turbo-como-4-0",
                "ev-trek-district-plus-9",
                "ev-cube-supreme-deluxe-one-625",
                "ev-gepida-bonum-edge-nexus-8c",
            ],
            "checkedAt": ACCESS,
            "table": table_json(comfort_ids),
            "bodyMarkdown": cmp_comfort,
        },
    ]

    for a in explainers + comparisons:
        write_md(a["slug"], a["bodyMarkdown"])

    dump(
        "articles.json",
        {"accessedAt": ACCESS, "explainers": explainers, "comparisons": comparisons},
    )


def fix_meta():
    meta = load("meta.json")
    meta["package"] = "kerekparindex-content-pilot-v2"
    meta["notInScope"] = [
        "CMS",
        "live price/inventory DB",
        "model–store stock links without evidence",
    ]
    meta["statusSemantics"] = {
        "ellenőrzött": (
            "A közölt mezők forrással igazoltak a checked/accessed dátumon; "
            "feloldatlan ellentmondásos mező nem jelenik meg ellenőrzött tényként."
        ),
        "előkészített": (
            "Részleges vagy korlátozott forrás (pl. Scott), illetve archivált gyártói oldal "
            "olvasható specifikációval, de aktuális gyártás/elérhetőség nem igazolt."
        ),
        "hiányos": "Kritikus adat hiányzik a rekord publikálásához.",
    }
    meta["dataFlags"] = {
        "archivált": "Gyártói oldal archived jelölésű",
        "ellentmondás": "Ugyanazon forráson belül feloldatlan mezőütközés",
        "hiányzó_adat": "Egyes mezők null + missingReason",
    }
    gaps = meta.get("gaps") or {}
    loc_gaps = list(gaps.get("locations") or [])
    loc_gaps = [
        g
        for g in loc_gaps
        if "Rekord Bike szerviz" not in g
    ]
    loc_gaps.append(
        "Rekord Bike szerviz: szervezeti oldal van, telephelyi hozzárendelés nélkül — "
        "szerviz szolgáltatás mindkét telephelyről visszatartva (előkészített org-jegyzet)."
    )
    gaps["locations"] = loc_gaps
    meta["gaps"] = gaps
    meta["heldBack"] = [
        {
            "id": "svc-rekord-*-szerviz",
            "reason": "Nincs telephely-specifikus szervizbizonyíték",
        },
        {
            "id": "brand-scott",
            "reason": "Előkészített: aktuális hivatalos HU importer URL hiányzik",
            "ui": "Márkalistán megjelenik előkészített jelzéssel",
        },
        {
            "id": "external brands (Bianchi, Marin, …)",
            "reason": "Nincs stabil brandId a 10-es katalógusban — researchNotes-ban",
        },
        {
            "id": "model–store links",
            "reason": "Nincs igazolt modell–készlet/kipróbálás kapcsolat",
        },
    ]
    # counts refresh roughly
    meta["counts"]["evidence"] = len(load("evidence.json")["items"])
    meta["counts"]["services"] = len(load("services.json")["items"])
    dump("meta.json", meta)


def fix_schema_readme():
    schema = """# KERÉKPÁRINDEX tartalmi séma — pilot v2

Importálható, fájlalapú csomag.

## Státuszértékek

| Érték | Jelentés |
| --- | --- |
| `ellenőrzött` | Forrással igazolt mezők; feloldatlan ellentmondás nem tényként jelenik meg |
| `előkészített` | Részleges forrás vagy archivált gyártói oldal |
| `hiányos` | Kritikus adat hiányzik a publikáláshoz |

## Adatjelzők (`dataFlags`)

`archivált` · `ellentmondás` · `hiányzó_adat`

## Entitások

| Entitás | Fájl | Kapcsolatok |
| --- | --- | --- |
| Brand | `brands.json` | ← products.brandId, locations.brandLinks.brandId |
| Organization | `organizations.json` | ← locations.organizationId |
| Location | `locations.json` | brandLinks (sells_brand + evidenceId); researchNotes elkülönítve |
| Service | `services.json` | locationId; telephelyhez kötött `sourceUrl` (és indokolt esetben evidence) |
| Product / Variant | `products.json` / `variants.json` | evidenceIds; unresolvedFields |
| Article | `articles.json` + `articles/*.md` | evidenceIds; JSON body = MD |
| Evidence | `evidence.json` | supports: entitás vagy entitás.mező |

## Szolgáltatásfelvétel (eladas / szerviz / e-bike-szerviz)

- Szolgáltatás **nem** kaphat alapértelmezett „igazolt” értéket felvételkor vagy importkor.
- Az **eladás** és a **szerviz** külön állítás: mindegyikhez saját, az adott telephelyhez kötött bizonyíték kell.
- Publikált szolgáltatásrekord kötelező mezője: nem üres `sourceUrl` (a forrás URL-je).
- A `verify-content-pilot.py` jelzi, ha publikált szolgáltatásnak nincs ilyen bizonyítékhivatkozása.
- A hivatkozás **tartalmi** megfelelőségét (pl. valóban az adott címen szervizelnek-e) külön kell ellenőrizni; a URL puszta megléte **nem** bizonyítja az állítást.
- Többtelephelyes cég központi szolgáltatáslistája nem rendelhető automatikusan minden fiókhoz.

## Publikus vs. kutatási megjegyzés

- `notes`: rövid, publikálható magyarázat
- `researchNotes`: belső / katalóguson kívüli állítások — a felület nem mutatja tényként

## Nem állított kapcsolatok

- `sells_brand` ≠ hivatalos márkakereskedő
- márkakínálat ≠ modellkészlet ≠ kipróbálhatóság
- szervezeti szervizoldal ≠ telephelyi szerviz
- üzlet ≠ automatikus szerviz
"""
    (CONTENT / "schema.md").write_text(schema, encoding="utf-8")


def build_content_js():
    """Publishable bundle for the static site."""
    brands = load("brands.json")["items"]
    locations = load("locations.json")["items"]
    services = load("services.json")["items"]
    products = load("products.json")["items"]
    variants = load("variants.json")["items"]
    articles = load("articles.json")
    evidence = {e["id"]: e for e in load("evidence.json")["items"]}
    meta = load("meta.json")

    # Publish filter
    pub_brands = [b for b in brands if b.get("status") in ("ellenőrzött", "előkészített")]
    pub_locs = [l for l in locations if l.get("status") == "ellenőrzött"]
    pub_services = [s for s in services]  # already filtered Rekord szerviz
    pub_products = [p for p in products if p.get("status") in ("ellenőrzött", "előkészített")]
    pub_variants = [v for v in variants if v.get("status") in ("ellenőrzött", "előkészített")]

    svc_by_loc = {}
    for s in pub_services:
        svc_by_loc.setdefault(s["locationId"], []).append(s)

    brand_locs = {}
    for loc in pub_locs:
        for bl in loc.get("brandLinks") or []:
            if bl.get("inCatalog") and bl.get("brandId"):
                brand_locs.setdefault(bl["brandId"], []).append(
                    {
                        "locationId": loc["id"],
                        "name": loc["name"],
                        "city": (loc.get("address") or {}).get("city"),
                        "relation": bl.get("relation"),
                        "disclaimer": DISCLAIMER,
                    }
                )

    def public_brand(b):
        out = {k: v for k, v in b.items() if k not in ("researchNotes",)}
        note = out.get("notes")
        if note and any(
            x in note.lower()
            for x in ("missing_reason", "fetch", "evidence", "incapsula", "html")
        ):
            out["notes"] = None
        return out

    def public_location(l):
        return {
            k: v
            for k, v in l.items()
            if k not in ("researchNotes", "notes")
        }

    def public_variant(v):
        out = dict(v)
        # Keep missingReason internally in JSON source; drop researchy keys from UI bundle
        out.pop("researchNotes", None)
        return out

    bundle = {
        "generatedAt": ACCESS,
        "package": meta.get("package"),
        "notice": (
            "A márka–üzlet kapcsolat azt jelenti, hogy az üzlet a márkát forgalmazza. "
            "Ez nem készletígéret és nem kipróbálási ígéret. Élő ár- vagy készletadatbázis nincs."
        ),
        "naLabel": NA,
        "brands": [public_brand(b) for b in pub_brands],
        "locations": [public_location(l) for l in pub_locs],
        "servicesByLocation": svc_by_loc,
        "products": pub_products,
        "variants": [public_variant(v) for v in pub_variants],
        "explainers": articles["explainers"],
        "comparisons": articles["comparisons"],
        "shopsByBrand": brand_locs,
        "heldBack": meta.get("heldBack") or [],
        "evidence": {
            eid: {"url": e["url"], "pageTitle": e.get("pageTitle"), "status": e.get("status")}
            for eid, e in evidence.items()
        },
    }

    js_path = ROOT / "data" / "content.js"
    js_path.write_text(
        "/**\n * Publikált tartalom (generált). Forrás: content/*.json\n"
        " * Frissítés: python3 scripts/apply-content-pilot-v2.py\n */\n"
        "window.KEREKPARINDEX_CONTENT = "
        + json.dumps(bundle, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )
    print("Wrote", js_path)


def main():
    raw = load("_research/locations-raw.json")
    fix_evidence()
    fix_locations(raw["locations"], load("evidence.json")["items"])
    fix_services()
    fix_variants()
    fix_products()
    fix_articles()
    fix_meta()
    fix_schema_readme()
    build_content_js()
    print("content pilot v2 structural apply done")


if __name__ == "__main__":
    main()
