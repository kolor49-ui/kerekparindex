#!/usr/bin/env python3
"""Initialize / refresh durable geographic collection registry from published locations."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = CONTENT / "_research" / "geo-registry.json"
ACCESS = date.today().isoformat()

# 19 vármegyék + Budapest (separate)
UNITS = [
    ("Budapest", None, True),
    ("Bács-Kiskun", "Kecskemét", False),
    ("Baranya", "Pécs", False),
    ("Békés", "Békéscsaba", False),
    ("Borsod-Abaúj-Zemplén", "Miskolc", False),
    ("Csongrád-Csanád", "Szeged", False),
    ("Fejér", "Székesfehérvár", False),
    ("Győr-Moson-Sopron", "Győr", False),
    ("Hajdú-Bihar", "Debrecen", False),
    ("Heves", "Eger", False),
    ("Jász-Nagykun-Szolnok", "Szolnok", False),
    ("Komárom-Esztergom", "Tatabánya", False),
    ("Nógrád", "Salgótarján", False),
    ("Pest", None, False),
    ("Somogy", "Kaposvár", False),
    ("Szabolcs-Szatmár-Bereg", "Nyíregyháza", False),
    ("Tolna", "Szekszárd", False),
    ("Vas", "Szombathely", False),
    ("Veszprém", "Veszprém", False),
    ("Zala", "Zalaegerszeg", False),
]

CITY_UNIT = {
    "Tiszaújváros": "Borsod-Abaúj-Zemplén",
    "Mezőkövesd": "Borsod-Abaúj-Zemplén",
    "Bátonyterenye": "Nógrád",
    "Tát": "Komárom-Esztergom",
    "Tótkomlós": "Békés",
    "Kalocsa": "Bács-Kiskun",
    "Budaörs": "Pest",
    "Biatorbágy": "Pest",
    "Veresegyház": "Pest",
    "Törökbálint": "Pest",
    "Nagykáta": "Pest",
    "Gyömrő": "Pest",
    "Göd": "Pest",
    "Budakeszi": "Pest",
    "Budapest": "Budapest",
    "Érd": "Pest",
    "Vác": "Pest",
    "Szentendre": "Pest",
    "Gödöllő": "Pest",
    "Cegléd": "Pest",
    "Szigetszentmiklós": "Pest",
    "Dunakeszi": "Pest",
    "Vecsés": "Pest",
    "Kiskunlacháza": "Pest",
    "Ócsa": "Pest",
    "Monor": "Pest",
    "Szigetszentmiklós": "Pest",
    "Paks": "Tolna",
    "Esztergom": "Komárom-Esztergom",
    "Tatabánya": "Komárom-Esztergom",
    "Tata": "Komárom-Esztergom",
    "Komárom": "Komárom-Esztergom",
    "Győr": "Győr-Moson-Sopron",
    "Sopron": "Győr-Moson-Sopron",
    "Mosonmagyaróvár": "Győr-Moson-Sopron",
    "Szombathely": "Vas",
    "Körmend": "Vas",
    "Sárvár": "Vas",
    "Zalaegerszeg": "Zala",
    "Nagykanizsa": "Zala",
    "Keszthely": "Zala",
    "Veszprém": "Veszprém",
    "Pápa": "Veszprém",
    "Balatonfüred": "Veszprém",
    "Ajka": "Veszprém",
    "Siófok": "Somogy",
    "Kaposvár": "Somogy",
    "Pécs": "Baranya",
    "Mohács": "Baranya",
    "Szekszárd": "Tolna",
    "Paks": "Tolna",
    "Székesfehérvár": "Fejér",
    "Dunaújváros": "Fejér",
    "Velence": "Fejér",
    "Gárdony": "Fejér",
    "Szeged": "Csongrád-Csanád",
    "Hódmezővásárhely": "Csongrád-Csanád",
    "Szentes": "Csongrád-Csanád",
    "Makó": "Csongrád-Csanád",
    "Kecskemét": "Bács-Kiskun",
    "Baja": "Bács-Kiskun",
    "Kiskunfélegyháza": "Bács-Kiskun",
    "Békéscsaba": "Békés",
    "Gyula": "Békés",
    "Orosháza": "Békés",
    "Szolnok": "Jász-Nagykun-Szolnok",
    "Tiszafüred": "Jász-Nagykun-Szolnok",
    "Jászberény": "Jász-Nagykun-Szolnok",
    "Debrecen": "Hajdú-Bihar",
    "Hajdúböszörmény": "Hajdú-Bihar",
    "Nyíregyháza": "Szabolcs-Szatmár-Bereg",
    "Miskolc": "Borsod-Abaúj-Zemplén",
    "Ózd": "Borsod-Abaúj-Zemplén",
    "Kazincbarcika": "Borsod-Abaúj-Zemplén",
    "Eger": "Heves",
    "Gyöngyös": "Heves",
    "Hatvan": "Heves",
    "Salgótarján": "Nógrád",
    "Balassagyarmat": "Nógrád",
}


def main() -> None:
    locs = json.loads((CONTENT / "locations.json").read_text(encoding="utf-8"))["items"]
    by_unit_city: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for loc in locs:
        city = (loc.get("address") or {}).get("city") or "?"
        unit = CITY_UNIT.get(city, "?")
        by_unit_city[unit][city].append(
            {"id": loc["id"], "name": loc["name"], "status": loc.get("status")}
        )

    prev = {}
    if OUT.exists():
        prev = json.loads(OUT.read_text(encoding="utf-8"))

    units = []
    for name, seat, is_bp in UNITS:
        cities_prev = {
            c["name"]: c
            for c in ((prev.get("units") or [{}]) and [])
        }
        # rebuild from prev structure if present
        old_unit = next((u for u in (prev.get("units") or []) if u.get("name") == name), None)
        old_cities = {c["name"]: c for c in (old_unit or {}).get("cities") or []}

        city_entries = []
        published_cities = by_unit_city.get(name, {})
        all_city_names = set(published_cities) | set(old_cities)
        if seat:
            all_city_names.add(seat)

        for city in sorted(all_city_names):
            pubs = published_cities.get(city) or []
            old = old_cities.get(city) or {}
            research_status = old.get("researchStatus")
            if pubs:
                research_status = "has_published"
            elif research_status in ("researched_no_verified", "in_progress", "not_researched"):
                pass
            else:
                research_status = "not_researched"
            city_entries.append(
                {
                    "name": city,
                    "isCountySeat": bool(seat and city == seat),
                    "researchStatus": research_status,
                    # not_researched | in_progress | researched_no_verified | has_published
                    "publishedLocationIds": [p["id"] for p in pubs],
                    "publishedCount": len(pubs),
                    "notes": old.get("notes"),
                }
            )

        # Budapest districts placeholder
        districts = None
        if is_bp:
            districts = (old_unit or {}).get("districts") or [
                {
                    "id": f"bp-{i:02d}",
                    "name": f"Budapest {i}. kerület",
                    "researchStatus": "not_researched",
                    "publishedLocationIds": [],
                }
                for i in range(1, 24)
            ]
            # tag published BP locs into districts if address has kerület — leave for later
            for d in districts:
                if "publishedLocationIds" not in d:
                    d["publishedLocationIds"] = []

        units.append(
            {
                "name": name,
                "type": "capital" if is_bp else "varmegye",
                "seat": seat,
                "cities": city_entries,
                "districts": districts,
                "publishedTotal": sum(c["publishedCount"] for c in city_entries),
            }
        )

    # Priority queue: seats with <3, units with few pubs, not_researched seats
    priority = []
    for u in units:
        if u["type"] == "capital":
            if u["publishedTotal"] < 20:
                priority.append(
                    {
                        "unit": u["name"],
                        "reason": "Budapest kerületenkénti bővítés",
                        "published": u["publishedTotal"],
                    }
                )
            continue
        seat = u.get("seat")
        seat_row = next((c for c in u["cities"] if c["name"] == seat), None)
        if seat_row and seat_row["publishedCount"] < 3:
            priority.append(
                {
                    "unit": u["name"],
                    "city": seat,
                    "reason": f"székhely <3 (most {seat_row['publishedCount']})",
                    "published": seat_row["publishedCount"],
                }
            )
        elif u["publishedTotal"] < 2:
            priority.append(
                {
                    "unit": u["name"],
                    "reason": f"vármegye kevés publikált ({u['publishedTotal']})",
                    "published": u["publishedTotal"],
                }
            )

    doc = {
        "accessedAt": ACCESS,
        "schemaNote": (
            "researchStatus: not_researched | in_progress | pass_incomplete | researched_no_verified | has_published. "
            "researched_no_verified ≠ «nincs ott üzlet». "
            "Egyetlen üres keresés ≠ lezárt település. "
            "Jelölt kimenetek (research-ledger.json): settlement_not_searched | searched_not_found | "
            "found_source_unreachable | found_excluded | pending_verification | published. "
            "Saját weboldal hiánya nem kizáró ok; Facebook célzottan is keresendő."
        ),
        "publishedLocationCount": len(locs),
        "units": units,
        "priorityQueue": priority,
        "nextContinuation": prev.get("nextContinuation")
        or {
            "batchHint": "Nógrád / Jász-Nagykun-Szolnok / Békés / Borsod székhelypótlás + kisebb városok",
            "afterCommit": None,
        },
        "brandBacklogPath": "_research/brand-backlog.json",
        "candidatesPath": "_research/candidates.json",
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "units": len(units),
                "published": len(locs),
                "priority": len(priority),
                "path": str(OUT),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
