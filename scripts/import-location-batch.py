#!/usr/bin/env python3
"""Import a verified location research batch into content/*.json + locations-raw."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ACCESS_DEFAULT = "2026-10-10"
DISCLAIMER = (
    "A márka forgalmazása nem jelenti automatikusan, hogy egy adott modell "
    "raktáron van, vagy kipróbálható."
)

def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def dump(name: str, data) -> None:
    (CONTENT / name).write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def brand_name_to_id() -> dict[str, str]:
    """Resolve from live brands.json (plus common aliases)."""
    mapping = {}
    for b in load("brands.json")["items"]:
        mapping[(b.get("name") or "").strip().lower()] = b["id"]
        mapping[(b.get("slug") or "").strip().lower()] = b["id"]
    # aliases
    mapping.update(
        {
            "cube": "brand-cube",
            "ktm": "brand-ktm",
            "ktm bike industries": "brand-ktm",
            "ktm bikes": "brand-ktm",
        }
    )
    return {k: v for k, v in mapping.items() if k}


def slugify(s: str) -> str:
    s = s.lower().strip()
    repl = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ö": "o",
        "ő": "o",
        "ú": "u",
        "ü": "u",
        "ű": "u",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:48]


def resolve_brand(name: str, mapping: dict[str, str]):
    return mapping.get((name or "").strip().lower())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    access = batch.get("accessedAt") or ACCESS_DEFAULT
    brand_map = brand_name_to_id()

    orgs = load("organizations.json")
    locs = load("locations.json")
    svcs = load("services.json")
    ev = load("evidence.json")
    raw = load("_research/locations-raw.json")
    coverage = CONTENT / "_research" / "coverage-summary.json"
    brand_backlog_path = CONTENT / "_research" / "brand-backlog.json"
    if brand_backlog_path.exists():
        brand_backlog = json.loads(brand_backlog_path.read_text(encoding="utf-8"))
    else:
        brand_backlog = {"accessedAt": access, "items": []}

    org_ids = {o["id"] for o in orgs["items"]}
    loc_ids = {l["id"] for l in locs["items"]}
    # address fingerprint for dup check
    addr_fp = {
        (
            (l.get("address") or {}).get("city", "").lower(),
            re.sub(r"\s+", " ", ((l.get("address") or {}).get("raw") or "").lower()),
        )
        for l in locs["items"]
    }

    added = []
    skipped = []
    held = list(batch.get("heldBack") or [])

    raw_locs = raw.setdefault("locations", [])
    raw_by_id = {l["id"]: l for l in raw_locs}

    for item in batch.get("items") or []:
        if item.get("heldBack"):
            held.append(
                {
                    "name": item.get("name"),
                    "city": item.get("city"),
                    "reason": item.get("heldBackReason") or "heldBack flag",
                    "candidateUrl": (item.get("evidence") or {}).get("url"),
                }
            )
            continue

        slug = item.get("idSlug") or slugify(item["name"] + "-" + item["city"])
        loc_id = "loc-" + slug
        org_id = "org-" + slug
        city = item["city"]
        address_raw = item["addressRaw"]
        fp = (city.lower(), re.sub(r"\s+", " ", address_raw.lower()))
        if loc_id in loc_ids:
            skipped.append((loc_id, "id exists"))
            continue
        if fp in addr_fp:
            skipped.append((loc_id, "address duplicate"))
            continue
        if not address_raw or not city or not item.get("name"):
            skipped.append((loc_id, "missing required"))
            continue
        contact_ok = bool(item.get("website") or item.get("phone") or item.get("email"))
        if not contact_ok:
            skipped.append((loc_id, "no contact"))
            continue
        roles = item.get("roles") or []
        if not roles:
            skipped.append((loc_id, "no roles"))
            continue
        evidence = item.get("evidence") or {}
        if not evidence.get("url"):
            skipped.append((loc_id, "no evidence url"))
            continue
        # Do not invent roles: each role must be explicitly listed; never default to eladas+szerviz.
        # Callers must only include szerviz when location-level evidence supports it.

        eid = "ev-" + slug + "-" + access.replace("-", "")
        # ensure unique evidence id
        existing_eids = {e["id"] for e in ev["items"]}
        n = 1
        base_eid = eid
        while eid in existing_eids:
            n += 1
            eid = f"{base_eid}-{n}"

        supports = [loc_id, f"{loc_id}.address"]
        if item.get("openingHours"):
            supports.append(f"{loc_id}.openingHours")
        if item.get("phone"):
            supports.append(f"{loc_id}.phone")
        if item.get("email"):
            supports.append(f"{loc_id}.email")
        if item.get("website"):
            supports.append(f"{loc_id}.website")

        catalog_claims = []
        external_claims = []
        for c in item.get("brandClaims") or []:
            bid = resolve_brand(c.get("brand"), brand_map)
            claim = {
                "brand": c.get("brand"),
                "relation": c.get("relation") or "sells_brand",
                "sourceUrl": c.get("sourceUrl") or evidence["url"],
                "quote": c.get("quote") or "",
            }
            if bid:
                catalog_claims.append(claim)
                supports.append(f"{loc_id}.brandLinks.{c.get('brand')}")
            else:
                external_claims.append(claim)
                # backlog out-of-catalog bike brands mentioned at shops
                brand_backlog.setdefault("items", []).append(
                    {
                        "name": c.get("brand"),
                        "seenAtLocation": loc_id,
                        "sourceUrl": claim["sourceUrl"],
                        "quote": claim["quote"],
                        "accessedAt": access,
                        "status": "candidate",
                    }
                )

        if org_id not in org_ids:
            orgs["items"].append(
                {
                    "id": org_id,
                    "name": item["name"],
                    "legalName": None,
                    "website": item.get("website"),
                    "notes": None,
                }
            )
            org_ids.add(org_id)

        loc = {
            "id": loc_id,
            "organizationId": org_id,
            "name": item["name"],
            "address": {
                "raw": address_raw,
                "city": city,
                "postalCode": None,
                "street": None,
            },
            "website": item.get("website"),
            "phone": item.get("phone") or [],
            "email": item.get("email") or [],
            "coordinates": None,
            "status": "ellenőrzött",
            "evidenceIds": [eid],
            "notes": item.get("notes"),
            "brandLinks": [],
            "researchNotes": {
                "externalBrandClaims": [
                    {
                        "brandName": x["brand"],
                        "relation": x["relation"],
                        "sourceUrl": x["sourceUrl"],
                        "quote": x["quote"],
                        "note": "Katalóguson kívüli márka — nincs stabil brandId ebben a körben.",
                    }
                    for x in external_claims
                ],
                "excludedClaims": [],
            },
        }
        if item.get("openingHours"):
            loc["openingHours"] = item["openingHours"]

        locs["items"].append(loc)
        loc_ids.add(loc_id)
        addr_fp.add(fp)

        role_evidence = item.get("roleEvidence") or {}
        deferred_roles = []
        for role in roles:
            if role in ("kolcsonzes", "kolcsonzo", "átveteli-pont", "atveteli-pont"):
                deferred_roles.append(role)
                continue
            role_slug = (
                role.replace("é", "e")
                .replace("á", "a")
                .replace("ö", "o")
                .replace("ő", "o")
                .replace("ü", "u")
                .replace("ű", "u")
            )
            re_src = role_evidence.get(role) or {}
            src = re_src.get("url") or evidence["url"]
            svcs["items"].append(
                {
                    "id": f"svc-{slug}-{role_slug}",
                    "locationId": loc_id,
                    "role": role,
                    "sourceUrl": src,
                }
            )
            supports.append(f"svc-{slug}-{role_slug}")
        if deferred_roles:
            loc["researchNotes"]["deferredRoles"] = [
                {
                    "role": r,
                    "note": "A jelenlegi publikus modellben nem szerepel; belső jelöltként őrizve.",
                    "sourceUrl": evidence["url"],
                }
                for r in deferred_roles
            ]

        ev["items"].append(
            {
                "id": eid,
                "url": evidence["url"],
                "pageTitle": evidence.get("pageTitle") or item["name"],
                "accessedAt": access,
                "supports": supports,
                "status": "ellenőrzött",
            }
        )

        raw_entry = {
            "id": loc_id,
            "organizationId": org_id,
            "name": item["name"],
            "address": address_raw,
            "city": city,
            "website": item.get("website"),
            "phone": item.get("phone") or [],
            "email": item.get("email") or [],
            "status": "ellenőrzött",
            "brandClaims": catalog_claims + external_claims,
            "notes": item.get("notes"),
        }
        if loc_id in raw_by_id:
            raw_by_id[loc_id].update(raw_entry)
        else:
            raw_locs.append(raw_entry)
            raw_by_id[loc_id] = raw_entry

        added.append(loc_id)

    # coverage summary
    from collections import Counter

    cities = Counter((l.get("address") or {}).get("city") for l in locs["items"])
    summary = {
        "accessedAt": access,
        "totalLocations": len(locs["items"]),
        "budapest": cities.get("Budapest", 0),
        "cities": dict(sorted(cities.items(), key=lambda x: (-x[1], x[0] or ""))),
        "lastBatch": batch.get("batchId"),
        "lastBatchAdded": len(added),
        "lastBatchSkipped": skipped,
        "heldBackCount": len(held),
        "heldBackSample": held[:40],
    }

    if args.dry_run:
        print(json.dumps({"wouldAdd": added, "skipped": skipped, "held": len(held)}, ensure_ascii=False, indent=2))
        return 0

    locs["accessedAt"] = access
    orgs["accessedAt"] = access
    svcs["accessedAt"] = access
    ev["accessedAt"] = access
    ev["items"] = sorted(ev["items"], key=lambda e: e["id"])

    dump("organizations.json", orgs)
    dump("locations.json", locs)
    dump("services.json", svcs)
    dump("evidence.json", ev)
    dump("_research/locations-raw.json", raw)
    brand_backlog["accessedAt"] = access
    brand_backlog_path.write_text(
        json.dumps(brand_backlog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    coverage.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # append held-back log
    held_path = CONTENT / "_research" / "held-back-locations.json"
    if held_path.exists():
        prev = json.loads(held_path.read_text(encoding="utf-8"))
    else:
        prev = {"items": []}
    prev["accessedAt"] = access
    prev["items"].extend(held)
    held_path.write_text(json.dumps(prev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "added": len(added),
                "skipped": len(skipped),
                "heldBack": len(held),
                "totalLocations": len(locs["items"]),
                "ids": added,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
