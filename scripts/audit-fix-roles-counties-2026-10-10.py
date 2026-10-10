#!/usr/bin/env python3
"""Apply szerviz evidence audit, fix county summary, promote verified held-backs."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ACCESS = "2026-10-10"

# Official 19 counties (vármegyék); Budapest is separate, not a vármegye.
VARMEGYEK = {
    "Bács-Kiskun",
    "Baranya",
    "Békés",
    "Borsod-Abaúj-Zemplén",
    "Csongrád-Csanád",
    "Fejér",
    "Győr-Moson-Sopron",
    "Hajdú-Bihar",
    "Heves",
    "Jász-Nagykun-Szolnok",
    "Komárom-Esztergom",
    "Nógrád",
    "Pest",
    "Somogy",
    "Szabolcs-Szatmár-Bereg",
    "Tolna",
    "Vas",
    "Veszprém",
    "Zala",
}

CITY_COUNTY = {
    "Budapest": None,  # not a vármegye
    "Érd": "Pest",
    "Vác": "Pest",
    "Szentendre": "Pest",
    "Esztergom": "Komárom-Esztergom",
    "Tatabánya": "Komárom-Esztergom",
    "Győr": "Győr-Moson-Sopron",
    "Sopron": "Győr-Moson-Sopron",
    "Szombathely": "Vas",
    "Körmend": "Vas",
    "Zalaegerszeg": "Zala",
    "Nagykanizsa": "Zala",
    "Keszthely": "Zala",
    "Veszprém": "Veszprém",
    "Pápa": "Veszprém",
    "Balatonfüred": "Veszprém",
    "Siófok": "Somogy",
    "Kaposvár": "Somogy",
    "Pécs": "Baranya",
    "Szekszárd": "Tolna",
    "Székesfehérvár": "Fejér",
    "Dunaújváros": "Fejér",
    "Velence": "Fejér",
    "Szeged": "Csongrád-Csanád",
    "Kecskemét": "Bács-Kiskun",
    "Békéscsaba": "Békés",
    "Szolnok": "Jász-Nagykun-Szolnok",
    "Tiszafüred": "Jász-Nagykun-Szolnok",
    "Debrecen": "Hajdú-Bihar",
    "Nyíregyháza": "Szabolcs-Szatmár-Bereg",
    "Miskolc": "Borsod-Abaúj-Zemplén",
    "Eger": "Heves",
    "Gyöngyös": "Heves",
    "Salgótarján": "Nógrád",
}


def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def dump(name: str, data) -> None:
    (CONTENT / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    audit = load("_research/szerviz-evidence-audit-2026-10-10.json")
    # Overrides: own-site / prior verified szerviz claims stronger than weak fetch of dealer card
    override_keep = {
        "svc-peppe-szerviz": "Saját oldal címe: «Peppe Kerékpár szaküzlet és szerviz»; Győr Nagy Imre út 91.",
        "svc-nelson-bike-veszprem-szerviz": (
            "Saját oldal (veszpremkerekpar.hu) korábban: «Kerékpárszaküzlet, Szerviz és Kölcsönző» "
            "Almádi út 40. (2026-10-10 fetch később captcha miatt blokkolt)."
        ),
    }
    # Also match by locId if svc id naming differs
    override_keep_loc = {
        "loc-peppe-gyor",
        "loc-nelson-bike-veszprem",
    }

    strip_ids = set()
    keep_ids = set()
    for row in audit["perLocation"]:
        sid = row["svcId"]
        lid = row["locId"]
        if sid in override_keep or lid in override_keep_loc:
            keep_ids.add(sid)
            continue
        if row["verdict"] == "strip":
            strip_ids.add(sid)
        else:
            keep_ids.add(sid)

    svcs = load("services.json")
    locs = load("locations.json")
    loc_by = {l["id"]: l for l in locs["items"]}
    ev = load("evidence.json")
    raw = load("_research/locations-raw.json")
    orgs = load("organizations.json")

    before = len(svcs["items"])
    stripped = []
    kept_svcs = []
    for s in svcs["items"]:
        if s["id"] in strip_ids and "szerviz" in (s.get("role") or ""):
            stripped.append(s)
            loc = loc_by.get(s["locationId"])
            if loc is not None:
                rn = dict(loc.get("researchNotes") or {})
                unver = list(rn.get("unverifiedServices") or [])
                unver.append(
                    {
                        "role": s.get("role"),
                        "sourceUrl": s.get("sourceUrl"),
                        "note": (
                            "Szervizszerep 2026-10-10-es forrásellenőrzés után nem volt "
                            "kellően igazolható az adott telephelyre; nem állítjuk, hogy nincs szerviz."
                        ),
                        "accessedAt": ACCESS,
                    }
                )
                rn["unverifiedServices"] = unver
                loc["researchNotes"] = rn
            continue
        kept_svcs.append(s)
    svcs["items"] = kept_svcs
    svcs["accessedAt"] = ACCESS

    # Promote Ga-Bike Kaposvár
    if "loc-gabike-kaposvar" not in loc_by:
        org_id = "org-gabike-kaposvar"
        loc_id = "loc-gabike-kaposvar"
        eid = "ev-gabike-kaposvar-20261010"
        orgs["items"].append(
            {
                "id": org_id,
                "name": "Ga-Bike Kerékpár Szaküzlet és Szerviz",
                "legalName": None,
                "website": "https://www.facebook.com/gabike2014",
                "notes": None,
            }
        )
        loc = {
            "id": loc_id,
            "organizationId": org_id,
            "name": "Ga-Bike Kerékpár Szaküzlet és Szerviz",
            "address": {
                "raw": "7400 Kaposvár, Fő utca 87.",
                "city": "Kaposvár",
                "postalCode": None,
                "street": None,
            },
            "website": "https://www.facebook.com/gabike2014",
            "phone": ["+36 20 373 8343"],
            "email": ["gabike2014@gmail.com"],
            "coordinates": None,
            "openingHours": "H–P 9:00–17:00",
            "status": "ellenőrzött",
            "evidenceIds": [eid],
            "notes": None,
            "brandLinks": [],
            "researchNotes": {
                "externalBrandClaims": [],
                "excludedClaims": [],
            },
        }
        locs["items"].append(loc)
        loc_by[loc_id] = loc
        kept_svcs.append(
            {
                "id": "svc-gabike-kaposvar-eladas",
                "locationId": loc_id,
                "role": "eladas",
                "sourceUrl": "https://bikefun.hu/shops/gabike",
            }
        )
        kept_svcs.append(
            {
                "id": "svc-gabike-kaposvar-szerviz",
                "locationId": loc_id,
                "role": "szerviz",
                "sourceUrl": "https://www.facebook.com/gabike2014",
                "notes": "Üzleti Facebook név és Tourinform Kaposvár listázás is szervizként jelöli.",
            }
        )
        ev["items"].append(
            {
                "id": eid,
                "url": "https://bikefun.hu/shops/gabike",
                "pageTitle": "GaBike - BikeFun",
                "accessedAt": ACCESS,
                "supports": [
                    loc_id,
                    f"{loc_id}.address",
                    f"{loc_id}.phone",
                    f"{loc_id}.email",
                    f"{loc_id}.openingHours",
                    "svc-gabike-kaposvar-eladas",
                ],
                "status": "ellenőrzött",
            }
        )
        ev["items"].append(
            {
                "id": "ev-gabike-fb-20261010",
                "url": "https://www.facebook.com/gabike2014",
                "pageTitle": "Ga-Bike Kerékpár Szaküzlet és Szerviz | Kaposvár | Facebook",
                "accessedAt": ACCESS,
                "supports": ["svc-gabike-kaposvar-szerviz", f"{loc_id}.website"],
                "status": "ellenőrzött",
            }
        )
        raw.setdefault("locations", []).append(
            {
                "id": loc_id,
                "organizationId": org_id,
                "name": "Ga-Bike Kerékpár Szaküzlet és Szerviz",
                "address": "7400 Kaposvár, Fő utca 87.",
                "city": "Kaposvár",
                "website": "https://www.facebook.com/gabike2014",
                "phone": ["+36 20 373 8343"],
                "email": ["gabike2014@gmail.com"],
                "status": "ellenőrzött",
                "brandClaims": [],
                "notes": None,
            }
        )

    # Promote Karikázzunk Velence as szerviz-only
    if "loc-karikazzunk-velence" not in loc_by:
        org_id = "org-karikazzunk-velence"
        loc_id = "loc-karikazzunk-velence"
        eid = "ev-karikazzunk-velence-20261010"
        orgs["items"].append(
            {
                "id": org_id,
                "name": "Karikázzunk kerékpár szerviz",
                "legalName": "Pátkai Tünde e.v.",
                "website": "https://karikazzunk.hu/szerviz/",
                "notes": None,
            }
        )
        loc = {
            "id": loc_id,
            "organizationId": org_id,
            "name": "Karikázzunk kerékpár szerviz",
            "address": {
                "raw": "2481 Velence, Ország út",
                "city": "Velence",
                "postalCode": None,
                "street": None,
            },
            "website": "https://karikazzunk.hu/szerviz/",
            "phone": ["+36 30 545 3508", "+36 70 397 3264"],
            "email": [],
            "coordinates": None,
            "status": "ellenőrzött",
            "evidenceIds": [eid],
            "notes": "A saját szervizoldal házszám nélkül «Velence Ország út» címet közöl.",
            "brandLinks": [],
            "researchNotes": {
                "externalBrandClaims": [],
                "excludedClaims": [],
            },
        }
        locs["items"].append(loc)
        loc_by[loc_id] = loc
        kept_svcs.append(
            {
                "id": "svc-karikazzunk-velence-szerviz",
                "locationId": loc_id,
                "role": "szerviz",
                "sourceUrl": "https://karikazzunk.hu/szerviz/",
            }
        )
        # e-bike diagnosztika mentioned — store as separate only if clear; page says Bosch/Bafang
        kept_svcs.append(
            {
                "id": "svc-karikazzunk-velence-ebike",
                "locationId": loc_id,
                "role": "e-bike-szerviz",
                "sourceUrl": "https://karikazzunk.hu/szerviz/",
                "notes": "Oldal szerint Bosch és Bafang diagnosztika; nem minden motorrendszer.",
            }
        )
        ev["items"].append(
            {
                "id": eid,
                "url": "https://karikazzunk.hu/szerviz/",
                "pageTitle": "Kerékpár szerviz Velence – Gyors javítás Velencei-tó",
                "accessedAt": ACCESS,
                "supports": [
                    loc_id,
                    f"{loc_id}.address",
                    f"{loc_id}.phone",
                    "svc-karikazzunk-velence-szerviz",
                    "svc-karikazzunk-velence-ebike",
                ],
                "status": "ellenőrzött",
            }
        )
        raw.setdefault("locations", []).append(
            {
                "id": loc_id,
                "organizationId": org_id,
                "name": "Karikázzunk kerékpár szerviz",
                "address": "2481 Velence, Ország út",
                "city": "Velence",
                "website": "https://karikazzunk.hu/szerviz/",
                "phone": ["+36 30 545 3508", "+36 70 397 3264"],
                "email": [],
                "status": "ellenőrzött",
                "brandClaims": [],
                "notes": "Házszám a forráson nem szerepel.",
            }
        )

    svcs["items"] = kept_svcs
    locs["accessedAt"] = ACCESS
    orgs["accessedAt"] = ACCESS
    ev["accessedAt"] = ACCESS
    ev["items"] = sorted(ev["items"], key=lambda e: e["id"])

    # Role tallies
    by = defaultdict(set)
    for s in svcs["items"]:
        by[s["locationId"]].add(s["role"])
    shop_only = svc_only = both = 0
    for lid in loc_by:
        rs = by.get(lid, set())
        has_e = "eladas" in rs
        has_s = any("szerviz" in r for r in rs)
        if has_e and has_s:
            both += 1
        elif has_e:
            shop_only += 1
        elif has_s:
            svc_only += 1

    # Coverage / counties — Budapest NOT counted as vármegye
    cities = Counter((l.get("address") or {}).get("city") for l in locs["items"])
    county_cities = defaultdict(set)
    unknown_cities = []
    for city in cities:
        if not city:
            continue
        if city == "Budapest":
            continue
        cty = CITY_COUNTY.get(city)
        if cty is None:
            unknown_cities.append(city)
        else:
            county_cities[cty].add(city)
    covered_counties = sorted(county_cities.keys())
    assert all(c in VARMEGYEK for c in covered_counties)
    assert "Budapest" not in covered_counties

    summary = {
        "accessedAt": ACCESS,
        "totalPublished": len(locs["items"]),
        "budapest": cities.get("Budapest", 0),
        "budapestSharePct": round(100 * cities.get("Budapest", 0) / len(locs["items"]), 1),
        "cityCount": len([c for c in cities if c]),
        "varmegyeCount": len(covered_counties),
        "varmegyeMax": 19,
        "countyCountErrorNote": (
            "A korábbi «20 vármegye (+ Budapest)» hibát az okozta, hogy a coverage-summary "
            "Budapestet is vármegyeként számolta a counties objektumban (19+1=20). "
            "Az adatállomány telephelyeihez nincs hibás county mező — csak a jelentés volt hibás."
        ),
        "cities": dict(sorted(cities.items(), key=lambda x: (-x[1], x[0] or ""))),
        "varmegyek": {k: sorted(v) for k, v in sorted(county_cities.items())},
        "unknownCities": unknown_cities,
        "roles": {
            "eladasOnly": shop_only,
            "szervizOnly": svc_only,
            "eladasAndSzerviz": both,
        },
        "szervizAudit": {
            "strippedServiceRows": len(stripped),
            "strippedIds": [s["id"] for s in stripped],
            "overrideKeep": list(override_keep.keys()),
        },
    }

    # Held-back refresh
    held = {
        "accessedAt": ACCESS,
        "promoted": [
            {
                "name": "Ga-Bike Kerékpár Szaküzlet és Szerviz",
                "city": "Kaposvár",
                "reason": "BikeFun hivatalos kereskedőoldal + üzleti Facebook + Tourinform",
            },
            {
                "name": "Karikázzunk kerékpár szerviz",
                "city": "Velence",
                "reason": "Saját szervizoldal címmel és telefonnal (házszám nélkül)",
            },
        ],
        "items": [
            {
                "name": "Westbike Kerékpárbolt és Szerviz",
                "city": "Szombathely",
                "reason": "Saját oldal csak karbantartási üzenet; cím/telefon nem igazolható onnan.",
                "candidateUrl": "https://www.westbike.hu/",
            },
            {
                "name": "BringaOtthon Árkádia Kerékpárbolt és Szerviz",
                "city": "Szombathely",
                "reason": "Nincs kellően ellenőrizhető saját vagy hivatalos üzleti oldal pontos címmel.",
                "candidateUrl": None,
            },
            {
                "name": "BlackBike Kerékpár Szerviz",
                "city": "Siófok",
                "reason": "Facebook 403; cím a saját forrásból nem ellenőrizhető. Későbbi szerviz/kölcsönző kör.",
                "candidateUrl": "https://www.facebook.com/blackbike.service/",
            },
            {
                "name": "HeloVelo Bike & Cafe",
                "city": "Pápa",
                "reason": "2026-os helyi hír szerint bezárt.",
                "candidateUrl": "https://www.infopapa.hu/hirek/olvas/ket-igenyes-kavezo-is-bezart-a-heten-papan-2026-06-18-160000",
            },
            {
                "name": "PedÁl Kerékpárüzlet és szerviz",
                "city": "Szombathely",
                "reason": "Csak gyűjtőlista/Facebook-jellegű nyom; cím és tevékenység nem kellően igazolt.",
                "candidateUrl": "https://veloregio.com/hu/kerekparos-szervizek/",
            },
            {
                "name": "Bikeland Kerékpár Bolt és Szerviz",
                "city": "Békéscsaba",
                "reason": "Csak Facebook/aggregátor; pontos hivatalos adatlap hiányzik.",
                "candidateUrl": "https://www.facebook.com/539958456163288",
            },
            {
                "name": "M-Bike Kerékpárszaküzlet és Szerviz",
                "city": "Tatabánya",
                "reason": "Domain nem elérhető; nincs pótló hivatalos forrás.",
                "candidateUrl": "https://mbike.hu/",
            },
            {
                "name": "Kerékpár Szaküzlet és Szerviz (Szőlősi út)",
                "city": "Tiszafüred",
                "reason": "Önkormányzati lista nem ellenőrizhető megbízhatóan.",
                "candidateUrl": None,
            },
            {
                "name": "Nyolcas Kerékpárszerviz és Szaküzlet",
                "city": "Vác",
                "reason": "Csak katalógus-oldal; nincs saját/hivatalos üzleti forrás.",
                "candidateUrl": "https://www.szakkatalogus.hu/",
            },
            {
                "name": "Localbike",
                "city": "Kecskemét",
                "reason": "localbike.hu 500/timeout; nem sikerült hivatalos adatot rögzíteni.",
                "candidateUrl": "https://www.localbike.hu/",
            },
            {
                "name": "BiciKlikk Szolnok",
                "city": "Szolnok",
                "reason": "Biciklikk saját üzleteink oldala csak Pécset sorol; ellentmondás a Neuzer partnerlistával.",
                "candidateUrl": "https://www.biciklikk.hu/uzleteink",
            },
            {
                "name": "Rent-E-Bike Miskolc",
                "city": "Miskolc",
                "reason": "Elsődlegesen kölcsönző — későbbi kölcsönzőrovat.",
                "candidateUrl": "https://www.kerekparszallitoberles.hu/",
                "deferredTo": "kolcsonzo",
            },
            {
                "name": "Csepi bicikli szerviz Agárd",
                "city": "Agárd",
                "reason": "Nincs saját/hivatalos oldal; csak gyűjtő/nyitvatartás oldalak.",
                "candidateUrl": None,
            },
        ],
    }

    dump("services.json", svcs)
    dump("locations.json", locs)
    dump("organizations.json", orgs)
    dump("evidence.json", ev)
    dump("_research/locations-raw.json", raw)
    dump("_research/coverage-summary.json", summary)
    dump("_research/held-back-locations.json", held)

    # meta counts
    meta = load("meta.json")
    if "counts" in meta:
        meta["counts"]["locations"] = len(locs["items"])
        meta["counts"]["organizations"] = len(orgs["items"])
        meta["counts"]["services"] = len(svcs["items"])
        meta["counts"]["evidence"] = len(ev["items"])
        meta["accessedAt"] = ACCESS
        dump("meta.json", meta)

    print(
        json.dumps(
            {
                "stripped": len(stripped),
                "servicesBefore": before,
                "servicesAfter": len(svcs["items"]),
                "locations": len(locs["items"]),
                "roles": summary["roles"],
                "varmegyeCount": summary["varmegyeCount"],
                "budapest": summary["budapest"],
                "heldRemaining": len(held["items"]),
                "promoted": len(held["promoted"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
