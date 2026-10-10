#!/usr/bin/env python3
"""KERÉKPÁRINDEX content pilot v2 verification (no network)."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "content"
ACCESS = "2026-10-10"
ALLOWED_STATUS = {"ellenőrzött", "előkészített", "hiányos"}


def load(name: str):
    with (ROOT / name).open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    results = {
        "date": ACCESS,
        "contentRoot": str(ROOT),
        "checks": [],
        "pass": True,
    }

    def check(name: str, ok: bool, detail=None):
        results["checks"].append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            results["pass"] = False

    required = [
        "meta.json",
        "brands.json",
        "organizations.json",
        "locations.json",
        "services.json",
        "products.json",
        "variants.json",
        "articles.json",
        "evidence.json",
        "schema.md",
        "README.md",
        "STATUS-SUMMARY.md",
    ]
    missing_files = [f for f in required if not (ROOT / f).exists()]
    check("required_files", not missing_files, missing_files or "all present")

    meta = load("meta.json")
    brands = load("brands.json")["items"]
    orgs = load("organizations.json")["items"]
    locations = load("locations.json")["items"]
    services_doc = load("services.json")
    services = services_doc["items"]
    products = load("products.json")["items"]
    variants_doc = load("variants.json")
    variants = variants_doc["items"]
    articles = load("articles.json")
    evidence = load("evidence.json")["items"]

    check("count_brands_at_least_10", len(brands) >= 10, len(brands))
    check("count_locations_at_least_20", len(locations) >= 20, len(locations))
    check("count_variants_12", len(variants) == 12, len(variants))
    check("count_explainers_6", len(articles.get("explainers", [])) == 6, len(articles.get("explainers", [])))
    check("count_comparisons_3", len(articles.get("comparisons", [])) == 3, len(articles.get("comparisons", [])))
    check(
        "count_comparison_groups_3",
        len(variants_doc.get("comparisonGroups") or []) == 3,
        len(variants_doc.get("comparisonGroups") or []),
    )

    cities = sorted(
        {
            (loc.get("address") or {}).get("city")
            for loc in locations
            if (loc.get("address") or {}).get("city")
        }
    )
    non_bp = [c for c in cities if c and c != "Budapest"]
    check("cities_at_least_6_total", len(cities) >= 6, cities)
    check("cities_non_budapest_at_least_5", len(non_bp) >= 5, non_bp)

    brand_ids = {b["id"] for b in brands}
    org_ids = {o["id"] for o in orgs}
    loc_ids = {l["id"] for l in locations}
    product_ids = {p["id"] for p in products}
    variant_ids = {v["id"] for v in variants}
    evidence_ids = {e["id"] for e in evidence}
    service_ids = {s["id"] for s in services}

    # Uniqueness
    for label, ids in [
        ("brands", [b["id"] for b in brands]),
        ("locations", [l["id"] for l in locations]),
        ("services", [s["id"] for s in services]),
        ("products", [p["id"] for p in products]),
        ("variants", [v["id"] for v in variants]),
        ("evidence", [e["id"] for e in evidence]),
    ]:
        dup = [i for i, n in Counter(ids).items() if n > 1]
        check(f"unique_ids_{label}", not dup, dup or "ok")

    brand_slugs = [b.get("slug") for b in brands]
    check("brand_slugs_unique", len(brand_slugs) == len(set(brand_slugs)), brand_slugs)

    # FK resolve
    check(
        "products_brandId_resolve",
        not [p["id"] for p in products if p.get("brandId") not in brand_ids],
        "ok",
    )
    check(
        "variants_productId_resolve",
        not [v["id"] for v in variants if v.get("productId") not in product_ids],
        "ok",
    )
    check(
        "locations_organizationId_resolve",
        not [l["id"] for l in locations if l.get("organizationId") not in org_ids],
        "ok",
    )
    check(
        "services_locationId_resolve",
        not [s.get("id") for s in services if s.get("locationId") not in loc_ids],
        "ok",
    )

    # Published services must carry an evidence URL reference (content adequacy is separate)
    missing_svc_source = [
        s.get("id")
        for s in services
        if not (isinstance(s.get("sourceUrl"), str) and s.get("sourceUrl").strip())
    ]
    check(
        "services_have_sourceUrl",
        not missing_svc_source,
        missing_svc_source[:20] or "ok",
    )

    # Brand links
    bad_links = []
    empty_links_with_claims = 0
    linked = 0
    for loc in locations:
        for bl in loc.get("brandLinks") or []:
            linked += 1
            if bl.get("inCatalog") and bl.get("brandId") not in brand_ids:
                bad_links.append((loc["id"], bl.get("brandId")))
            if not bl.get("sourceUrl") and not bl.get("evidenceId"):
                bad_links.append((loc["id"], "missing_source"))
            if bl.get("evidenceId") and bl["evidenceId"] not in evidence_ids:
                bad_links.append((loc["id"], bl.get("evidenceId")))
        if loc.get("evidenceIds"):
            for eid in loc["evidenceIds"]:
                if eid not in evidence_ids:
                    bad_links.append((loc["id"], eid))
        else:
            bad_links.append((loc["id"], "empty_evidenceIds"))
    check("brand_links_and_location_evidence", not bad_links, bad_links[:20] or f"ok linked={linked}")
    check("brand_links_at_least_8", linked >= 8, linked)

    # Rekord Bike (org) szerviz must not be auto-assigned to BP/Győr without site proof
    rekord_svc = [
        s["id"]
        for s in services
        if s.get("locationId") in ("loc-rekord-budapest", "loc-rekord-gyor")
        and "szerviz" in (s.get("role") or "")
    ]
    check("rekord_szerviz_not_on_locations", not rekord_svc, rekord_svc or "ok")

    # Variant evidence supports
    var_ev_missing = []
    for v in variants:
        eids = v.get("evidenceIds") or []
        if not eids:
            var_ev_missing.append(v["id"])
            continue
        for eid in eids:
            if eid not in evidence_ids:
                var_ev_missing.append((v["id"], eid))
                continue
            ev = next(e for e in evidence if e["id"] == eid)
            supports = ev.get("supports")
            if not supports:
                var_ev_missing.append((v["id"], eid, "empty_supports"))
            elif not any(str(s).startswith(v["id"]) for s in supports):
                var_ev_missing.append((v["id"], eid, "supports_mismatch"))
            if not ev.get("pageTitle"):
                var_ev_missing.append((v["id"], eid, "missing_pageTitle"))
    check("variant_evidence_supports_and_titles", not var_ev_missing, var_ev_missing[:15] or "ok")

    # Evidence pageTitle for location ev-01..28
    missing_titles = [
        e["id"]
        for e in evidence
        if e["id"].startswith("ev-")
        and e["id"][3:5].isdigit()
        and not e.get("pageTitle")
    ]
    check("location_evidence_pageTitles", not missing_titles, missing_titles or "ok")

    # Status vocabulary
    bad_status = []
    for label, items in [
        ("brands", brands),
        ("locations", locations),
        ("products", products),
        ("variants", variants),
        ("explainers", articles.get("explainers", [])),
        ("comparisons", articles.get("comparisons", [])),
        ("evidence", evidence),
    ]:
        for it in items:
            st = it.get("status")
            if st not in ALLOWED_STATUS:
                bad_status.append((label, it.get("id"), st))
    check("status_vocabulary", not bad_status, bad_status or "ok")

    # Publication readiness: publishable counts
    pub_brands = [b for b in brands if b["status"] in ("ellenőrzött", "előkészített")]
    pub_vars = [v for v in variants if v["status"] in ("ellenőrzött", "előkészített")]
    check("publishable_brands_at_least_10", len(pub_brands) >= 10, len(pub_brands))
    check("publishable_variants_12", len(pub_vars) == 12, len(pub_vars))

    # Articles: evidence + markdown parity
    md_dir = ROOT / "articles"
    md_files = list(md_dir.glob("*.md")) if md_dir.exists() else []
    check("article_markdown_files_9", len(md_files) == 9, [p.name for p in md_files])

    explainer_slugs = [a["slug"] for a in articles.get("explainers", [])]
    comparison_slugs = [a["slug"] for a in articles.get("comparisons", [])]
    missing_md = [
        s for s in explainer_slugs + comparison_slugs if not (md_dir / f"{s}.md").exists()
    ]
    check("article_md_matches_json_slugs", not missing_md, missing_md or "ok")

    body_mismatch = []
    for a in articles.get("explainers", []) + articles.get("comparisons", []):
        eids = a.get("evidenceIds") or []
        if a["type"] == "magyarazo" and len(eids) < 1:
            body_mismatch.append((a["id"], "no_evidence"))
        for eid in eids:
            if eid not in evidence_ids:
                body_mismatch.append((a["id"], eid))
        md_path = md_dir / f"{a['slug']}.md"
        if md_path.exists():
            md = md_path.read_text(encoding="utf-8").strip()
            body = (a.get("bodyMarkdown") or "").strip()
            if md != body:
                body_mismatch.append((a["id"], "md_json_mismatch"))
        if "null" in (a.get("bodyMarkdown") or "") and "Nincs ellenőrzött adat" not in (
            a.get("bodyMarkdown") or ""
        ):
            # allow URL null? prefer NA label — soft fail if raw `null` table cells remain
            if "| null |" in (a.get("bodyMarkdown") or "") or a.get("bodyMarkdown", "").count(" null ") > 0:
                body_mismatch.append((a["id"], "raw_null_in_body"))
    check("articles_evidence_and_md_parity", not body_mismatch, body_mismatch[:20] or "ok")

    # Comfort group rename
    group_ids = {g["id"] for g in variants_doc.get("comparisonGroups") or []}
    check("comparison_group_renamed_city_comfort", "cmp-city-comfort" in group_ids, sorted(group_ids))
    check("old_compact_group_removed", "cmp-compact-urban" not in group_ids, sorted(group_ids))

    # Trek weight wording in comparison
    comfort = next(
        (c for c in articles.get("comparisons", []) if c["id"] == "art-cmp-city-comfort"),
        None,
    )
    trek_ok = bool(
        comfort
        and "24,9 kg, akkumulátor nélkül" in (comfort.get("bodyMarkdown") or "")
    )
    check("trek_weight_phrase_in_comparison", trek_ok, "ok" if trek_ok else "missing")

    # Explainer professional sources (not only manuals hub)
    wh = next(a for a in articles["explainers"] if a["id"] == "art-exp-wh")
    check(
        "explainer_wh_has_bosch_batteries",
        "ev-bosch-batteries" in (wh.get("evidenceIds") or []),
        wh.get("evidenceIds"),
    )
    rng = next(a for a in articles["explainers"] if a["id"] == "art-exp-range")
    check(
        "explainer_range_has_range_assistant",
        "ev-bosch-range-assistant" in (rng.get("evidenceIds") or []),
        rng.get("evidenceIds"),
    )

    brand_via_product = set()
    prod_map = {p["id"]: p for p in products}
    for v in variants:
        p = prod_map.get(v.get("productId"))
        if p and p.get("brandId"):
            brand_via_product.add(p["brandId"])
    check("variants_cover_at_least_4_brands", len(brand_via_product) >= 4, sorted(brand_via_product))

    group_ok = True
    group_detail = []
    for g in variants_doc.get("comparisonGroups") or []:
        ids = g.get("variantIds") or []
        ok = 2 <= len(ids) <= 4 and all(i in variant_ids for i in ids)
        group_detail.append({"id": g.get("id"), "n": len(ids), "ok": ok})
        if not ok:
            group_ok = False
    check("comparison_groups_valid", group_ok, group_detail)

    def tally(items, key="status"):
        return dict(Counter((i.get(key) or "unknown") for i in items))

    status_summary = {
        "brands": tally(brands),
        "locations": tally(locations),
        "variants": tally(variants),
        "explainers": tally(articles.get("explainers", [])),
        "comparisons": tally(articles.get("comparisons", [])),
        "evidence": tally(evidence),
        "services": len(services),
    }
    results["statusSummary"] = status_summary
    results["counts"] = {
        "brands": len(brands),
        "organizations": len(orgs),
        "locations": len(locations),
        "services": len(services),
        "products": len(products),
        "variants": len(variants),
        "evidence": len(evidence),
        "explainers": len(articles.get("explainers", [])),
        "comparisons": len(articles.get("comparisons", [])),
        "articleMarkdown": len(md_files),
        "brandLinks": linked,
        "cities": cities,
    }
    results["conflicts"] = variants_doc.get("conflicts") or meta.get("conflicts") or []
    results["gaps"] = meta.get("gaps") or {}
    results["heldBack"] = meta.get("heldBack") or []
    results["failedChecks"] = [c["name"] for c in results["checks"] if not c["ok"]]

    out_json = ROOT / "VERIFY-RUN-RESULT.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Content pilot verification run (v2)",
        "",
        f"Date: {ACCESS}",
        f"Command: `python3 scripts/verify-content-pilot.py`",
        f"Result: **{'PASS' if results['pass'] else 'FAIL'}**",
        "",
        "## Counts",
        "",
        "```json",
        json.dumps(results["counts"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Status tallies",
        "",
        "```json",
        json.dumps(status_summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Checks",
        "",
    ]
    for c in results["checks"]:
        mark = "PASS" if c["ok"] else "FAIL"
        lines.append(f"- {mark}: `{c['name']}` — {c['detail']}")
    lines += [
        "",
        f"Conflicts recorded: {len(results['conflicts'])}",
        f"Held back: {len(results['heldBack'])}",
        "",
        "Raw JSON: `content/VERIFY-RUN-RESULT.json`",
        "",
    ]
    (ROOT / "VERIFY-RUN.md").write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "pass": results["pass"],
                "failed": results["failedChecks"],
                "counts": results["counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if results["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
