#!/usr/bin/env python3
"""Enrich existing 10 brands + 20 locations from re-checked official pages (2026-10-10)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ACCESS = "2026-10-10"


def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def dump(name: str, data) -> None:
    (CONTENT / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def upsert_evidence(items: list, entry: dict) -> None:
    by_id = {e["id"]: e for e in items}
    by_id[entry["id"]] = entry
    items[:] = sorted(by_id.values(), key=lambda e: e["id"])


def main() -> None:
    brands = load("brands.json")
    locations = load("locations.json")
    evidence = load("evidence.json")
    loc_by_id = {l["id"]: l for l in locations["items"]}

    # --- Evidence from this pass ---
    new_ev = [
        {
            "id": "ev-futurebike-scott-2026-10-10",
            "url": "https://futurebike.hu/marka/scott/",
            "pageTitle": "Scott kerékpárok – hivatalos márkakereskedés | Futurebike",
            "accessedAt": ACCESS,
            "supports": [
                "loc-futurebike-bartok.brandLinks.Scott",
                "loc-futurebike-bartok.openingHours",
                "loc-futurebike-bartok.email",
                "loc-futurebike-bartok.phone",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-k2shop-home-2026-10-10",
            "url": "https://k2shop.hu/",
            "pageTitle": "News K2 Shop - Bike Ski Snowboard products selling and maintaining",
            "accessedAt": ACCESS,
            "supports": [
                "loc-k2-pacsirtamezo.openingHours",
                "loc-k2-pacsirtamezo.phone",
                "loc-k2-pacsirtamezo.email",
                "loc-k2-pacsirtamezo.address",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-bikeart-kapcsolat-2026-10-10",
            "url": "https://www.bikeart.hu/kapcsolat.html",
            "pageTitle": "Kapcsolat – BikeArt Center",
            "accessedAt": ACCESS,
            "supports": [
                "loc-bikeart-csalogany.openingHours",
                "loc-bikeart-csalogany.phone",
                "loc-bikeart-csalogany.address",
                "loc-bikeart-kissjanos.openingHours",
                "loc-bikeart-kissjanos.phone",
                "loc-bikeart-kissjanos.address",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-peppe-home-2026-10-10",
            "url": "https://peppekerekpar.hu/",
            "pageTitle": "Peppe Kerékpár szaküzlet és szerviz Győr",
            "accessedAt": ACCESS,
            "supports": [
                "loc-peppe-gyor.openingHours",
                "loc-peppe-gyor.phone",
                "loc-peppe-gyor.email",
                "loc-peppe-gyor.address",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-vozzy-uzletunk-2026-10-10",
            "url": "https://www.vozzy.hu/spg/601152/Uzletunk",
            "pageTitle": "Üzletünk - Vozzy Bike & Snow",
            "accessedAt": ACCESS,
            "supports": [
                "loc-vozzy-debrecen.openingHours",
                "loc-vozzy-debrecen.phone",
                "loc-vozzy-debrecen.email",
                "loc-vozzy-debrecen.address",
                "loc-vozzy-debrecen.brandLinks.Merida",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-biciklikk-kapcsolat-2026-10-10",
            "url": "https://www.biciklikk.hu/kapcsolat",
            "pageTitle": "Kapcsolat - Biciklikk.hu",
            "accessedAt": ACCESS,
            "supports": [
                "loc-biciklikk-pecs.openingHours",
                "loc-biciklikk-pecs.phone",
                "loc-biciklikk-pecs.email",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-gepida-bonum-2026-10-10",
            "url": "https://gepida.hu/bonum-edge-nexus-8c-coaster-wh-28-13619",
            "pageTitle": "BONUM EDGE NEXUS 8C (COASTER) - Gepida",
            "accessedAt": ACCESS,
            "supports": ["var-gepida-bonum-edge-nexus-8c-coaster-400.brakes"],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-gepida-sirmium-2026-10-10",
            "url": "https://gepida.hu/gepida-sirmium-pro-deore-10-feher-11105",
            "pageTitle": "SIRMIUM PRO DEORE 10 - Gepida",
            "accessedAt": ACCESS,
            "supports": ["var-gepida-sirmium-pro-deore-10-500.tires"],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-giant-explore-2026-10-10",
            "url": "https://www.giant-bicycles.com/int/explore-eplus-1-stagger",
            "pageTitle": "Explore E+ 1 Stagger (2026) | Giant Bicycles International",
            "accessedAt": ACCESS,
            "supports": [
                "var-giant-explore-eplus-1-stagger-2026.drivetrain",
                "var-giant-explore-eplus-1-stagger-2026.modelYear",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-merida-espresso-2026-10-10",
            "url": "https://www.merida-bikes.com/en/bike/5675-7682/espresso-575-eq",
            "pageTitle": "Archived :: eSPRESSO 575 EQ - MERIDA BIKES",
            "accessedAt": ACCESS,
            "supports": [
                "var-merida-espresso-575-eq-750.weightKg",
                "var-merida-espresso-575-eq-750.status",
            ],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-scott-site-incapsula-2026-10-10",
            "url": "https://www.scott-sports.com/global/en/products/bike-bikes",
            "pageTitle": "Scott Sports bike products (fetch blocked / Incapsula)",
            "accessedAt": ACCESS,
            "supports": ["brand-scott.officialWebsite"],
            "status": "előkészített",
        },
        {
            "id": "ev-cube-eu-hu-2026-10-10",
            "url": "https://www.cube.eu/hu-hu",
            "pageTitle": "HOME | CUBE Bikes",
            "accessedAt": ACCESS,
            "supports": ["brand-cube.productCategories", "brand-cube.shortDescription"],
            "status": "ellenőrzött",
        },
        {
            "id": "ev-neuzer-home-2026-10-10",
            "url": "https://www.neuzer.hu",
            "pageTitle": "Neuzer Kerékpárok",
            "accessedAt": ACCESS,
            "supports": ["brand-neuzer.shortDescription", "brand-neuzer.hungaryRelatedWebsite"],
            "status": "ellenőrzött",
        },
    ]
    for e in new_ev:
        upsert_evidence(evidence["items"], e)

    # --- Brands polish (re-checked where noted) ---
    brand_updates = {
        "brand-cube": {
            "shortDescription": (
                "Német kerékpármárka: mountain, országúti, gravel, trekking, gyerek "
                "és több e-bike kategória. Hivatalos magyar nyelvű oldal: cube.eu/hu-hu; "
                "a cube-bikes.hu Cube kerékpárokat és kiegészítőket kínál."
            ),
            "evidenceIds_add": ["ev-cube-eu-hu-2026-10-10"],
        },
        "brand-giant": {
            "shortDescription": (
                "A Giant hivatalos magyar oldalán (giant-bicycles.com/hu) kerékpárok, "
                "kiegészítők és e-bike modellek szerepelnek."
            ),
        },
        "brand-trek": {
            "shortDescription": (
                "Nemzetközi Trek márka. Magyarországon a trek.hu (Genomed Kft., Budapest) "
                "forgalmaz Trek kerékpárokat, alkatrészeket és kiegészítőket, országos üzlethálózattal."
            ),
        },
        "brand-specialized": {
            "shortDescription": (
                "A Specialized hivatalos magyar nyelvű (/hu/en) oldala elérhető. "
                "A gyártó forgalmazói listáján Magyarország (Hauser Kerkpr Kft., Budapest) "
                "Specialized Hungaryként szerepel."
            ),
        },
        "brand-merida": {
            "shortDescription": (
                "A Merida hivatalos oldala a BikeFun-t nevezi meg magyarországi forgalmazóként. "
                "A bikefun.hu Merida híreket és modelleket közöl."
            ),
        },
        "brand-scott": {
            "shortDescription": (
                "Svájci kerékpármárka (MTB, országúti, gravel és e-bike kínálattal). "
                "A hivatalos gyártói oldal 2026-10-10-én nem volt ellenőrizhető. "
                "Magyarországi kereskedői jelenlét van (pl. Futurebike Scott márkaoldal), "
                "de aktuális hivatalos importőr-URL nélkül a márkalap előkészítés alatt áll."
            ),
            "evidenceIds_add": [
                "ev-scott-site-incapsula-2026-10-10",
                "ev-futurebike-scott-2026-10-10",
            ],
            "researchNotes": {
                "missing_reason": (
                    "officialWebsite fetch sikertelen (Incapsula) 2026-10-10. "
                    "Futurebike saját oldalán Scott márkaboltként jelenik meg; "
                    "ez nem helyettesíti a gyártói HU importer oldalt."
                ),
            },
        },
        "brand-cannondale": {
            "shortDescription": (
                "A Cannondale nemzetközi oldalán road, mountain, gravel, electric és kids kínálat szerepel. "
                "Magyarországon a cannondale-bikes.hu és a MALI Magyarország cannondale.hu oldala "
                "forgalmaz Cannondale kerékpárokat."
            ),
        },
        "brand-gepida": {
            "shortDescription": (
                "Magyar kerékpármárka: a gepida.hu szerint Magyarországon alapították, tervezik és gyártják. "
                "Trekking és e-MTB modellek; budapesti bemutatóterem: 1164 Budapest, Ostorhegy u. 4."
            ),
        },
        "brand-neuzer": {
            "shortDescription": (
                "Magyar kerékpármárka esztergomi székhellyel és gyártással, budapesti nagykereskedelmi raktárral "
                "(Acélcső utca — viszonteladó partnereknek). A lakossági rendelést a Viddabringát.hu-ra irányítják; "
                "a neuzer.hu-n e-MTB és e-trekking modellek is szerepelnek."
            ),
            "evidenceIds_add": ["ev-neuzer-home-2026-10-10"],
        },
        "brand-ktm": {
            "shortDescription": (
                "A KTM Fahrrad GmbH kerékpárokat és e-bike-okat gyárt (ktm-bikes.at). "
                "A ktmteam.hu a KTM kerékpárok magyarországi képviseleti oldala. "
                "Nem azonos a KTM AG motorkerékpár-gyártóval."
            ),
        },
    }

    for b in brands["items"]:
        u = brand_updates.get(b["id"])
        if not u:
            continue
        if "shortDescription" in u:
            b["shortDescription"] = u["shortDescription"]
        if "researchNotes" in u:
            b["researchNotes"] = u["researchNotes"]
        for eid in u.get("evidenceIds_add") or []:
            ids = list(b.get("evidenceIds") or [])
            if eid not in ids:
                ids.append(eid)
            b["evidenceIds"] = ids
    brands["accessedAt"] = ACCESS

    # --- Locations: hours + Scott link + website polish ---
    hours = {
        "loc-futurebike-bartok": "H–P 11:00–19:00, Szo 9:00–14:00, Vasárnap zárva",
        "loc-k2-pacsirtamezo": "H–Sze 10:00–18:00, Cs 10:00–19:00, P 10:00–18:00, Szo 10:00–15:00, Vasárnap zárva",
        "loc-bikeart-csalogany": "H–P 10:00–18:00, Szo 10:00–13:00",
        "loc-bikeart-kissjanos": "H–P 10:00–18:00",
        "loc-peppe-gyor": "H–P 9:00–18:00",
        "loc-vozzy-debrecen": "H–P 10:00–18:00, Szo 9:00–13:00 (Vasárnap csak téli szezonban 9:00–13:00)",
        "loc-biciklikk-pecs": "H–P 9:00–12:00 és 13:15–17:00, Szo 9:00–12:00",
    }
    hours_ev = {
        "loc-futurebike-bartok": "ev-futurebike-scott-2026-10-10",
        "loc-k2-pacsirtamezo": "ev-k2shop-home-2026-10-10",
        "loc-bikeart-csalogany": "ev-bikeart-kapcsolat-2026-10-10",
        "loc-bikeart-kissjanos": "ev-bikeart-kapcsolat-2026-10-10",
        "loc-peppe-gyor": "ev-peppe-home-2026-10-10",
        "loc-vozzy-debrecen": "ev-vozzy-uzletunk-2026-10-10",
        "loc-biciklikk-pecs": "ev-biciklikk-kapcsolat-2026-10-10",
    }

    # K2: prefer currently verified shop domain for contact page
    k2 = loc_by_id["loc-k2-pacsirtamezo"]
    k2["website"] = "https://k2shop.hu/"
    k2["email"] = ["k2@k2shop.hu"]
    # keep existing phones; align with re-check
    k2["phone"] = ["+36 1 453 0818", "+36 30 995 2728"]
    k2["address"]["raw"] = "1036 Budapest, Pacsirtamező u. 16."

    peppe = loc_by_id["loc-peppe-gyor"]
    peppe["email"] = ["info@peppekerekpar.hu"]
    peppe["phone"] = ["+36 96 419 507", "+36 30 204 6685"]
    peppe["address"]["raw"] = "9024 Győr, Nagy Imre út 91."

    vozzy = loc_by_id["loc-vozzy-debrecen"]
    vozzy["email"] = ["info@vozzy.hu"]
    vozzy["phone"] = ["+36 70 378 1657"]
    vozzy["address"]["raw"] = "4027 Debrecen, Böszörményi út 1."

    bikeart_c = loc_by_id["loc-bikeart-csalogany"]
    bikeart_c["phone"] = ["+36 1 457 6737"]
    bikeart_c["address"]["raw"] = "1027 Budapest, Csalogány utca 23-33."

    bikeart_k = loc_by_id["loc-bikeart-kissjanos"]
    bikeart_k["phone"] = ["+36 1 952 0432"]
    bikeart_k["address"]["raw"] = "1126 Budapest, Kiss János Alt. utca 25."

    for lid, summary in hours.items():
        loc = loc_by_id[lid]
        loc["openingHours"] = summary
        eid = hours_ev[lid]
        ids = list(loc.get("evidenceIds") or [])
        if eid not in ids:
            ids.append(eid)
        loc["evidenceIds"] = ids

    # Futurebike: Scott sells_brand (retail claim on own brand page — not stock)
    fb = loc_by_id["loc-futurebike-bartok"]
    fb["email"] = ["hello@futurebike.hu", "factorystore@gepida.hu"]
    links = list(fb.get("brandLinks") or [])
    if not any(b.get("brandId") == "brand-scott" for b in links):
        links.append(
            {
                "brandId": "brand-scott",
                "brandName": "Scott",
                "relation": "sells_brand",
                "sourceUrl": "https://futurebike.hu/marka/scott/",
                "quote": "Scott kerékpárok – hivatalos márkakereskedés",
                "evidenceId": "ev-futurebike-scott-2026-10-10",
                "disclaimer": (
                    "A márka forgalmazása nem jelenti automatikusan, hogy egy adott modell "
                    "raktáron van, vagy kipróbálható."
                ),
                "inCatalog": True,
            }
        )
    fb["brandLinks"] = links
    # note about gepida hours sources may differ — keep research, clear public note conflict
    fb["notes"] = (
        "gepida.hu és gepidastore.hu/futurebike.hu ugyanarra a címre hivatkozik; "
        "a nyitvatartást a futurebike.hu oldal alapján rögzítettük (2026-10-10)."
    )

    # Biciklikk: keep phone ambiguity in researchNotes, set hours + email
    bic = loc_by_id["loc-biciklikk-pecs"]
    bic["email"] = ["info@biciklikk.hu"]
    rn = dict(bic.get("researchNotes") or {})
    rn["phoneShopServiceLabel"] = (
        "A kapcsolat oldalon az üzlet/szerviz telefonszámok forrásonként felcserélve "
        "jelenhetnek meg — a nyilvános listában a korábbi, forráshoz kötött számok maradnak."
    )
    bic["researchNotes"] = rn

    locations["accessedAt"] = ACCESS
    evidence["accessedAt"] = ACCESS

    # Variants: reconfirm conflicts remain; update Giant model year display note via trim
    variants = load("variants.json")
    for v in variants["items"]:
        if v["id"] == "var-giant-explore-eplus-1-stagger-2026":
            v["modelYear"] = 2026
            if "modelYear" in (v.get("missingFields") or []):
                v["missingFields"] = [f for f in v["missingFields"] if f != "modelYear"]
            eids = list(v.get("evidenceIds") or [])
            if "ev-giant-explore-2026-10-10" not in eids:
                eids.append("ev-giant-explore-2026-10-10")
            v["evidenceIds"] = eids
            # keep drivetrainNote visitor wording from apply script
        if v["id"] == "var-merida-espresso-575-eq-750":
            eids = list(v.get("evidenceIds") or [])
            if "ev-merida-espresso-2026-10-10" not in eids:
                eids.append("ev-merida-espresso-2026-10-10")
            v["evidenceIds"] = eids
            # weight already 27.1 with M condition — confirmed archived page
        if v["id"] == "var-gepida-bonum-edge-nexus-8c-coaster-400":
            eids = list(v.get("evidenceIds") or [])
            if "ev-gepida-bonum-2026-10-10" not in eids:
                eids.append("ev-gepida-bonum-2026-10-10")
            v["evidenceIds"] = eids
        if v["id"] == "var-gepida-sirmium-pro-deore-10-500":
            eids = list(v.get("evidenceIds") or [])
            if "ev-gepida-sirmium-2026-10-10" not in eids:
                eids.append("ev-gepida-sirmium-2026-10-10")
            v["evidenceIds"] = eids
    variants["accessedAt"] = ACCESS

    dump("brands.json", brands)
    dump("locations.json", locations)
    dump("evidence.json", evidence)
    dump("variants.json", variants)
    print(
        "enriched: brands=%d locations=%d evidence=%d"
        % (len(brands["items"]), len(locations["items"]), len(evidence["items"]))
    )


if __name__ == "__main__":
    main()
