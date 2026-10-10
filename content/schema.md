# KERÉKPÁRINDEX tartalmi séma — pilot v2

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
| Service | `services.json` | locationId; telephelyi bizonyíték kell |
| Product / Variant | `products.json` / `variants.json` | evidenceIds; unresolvedFields |
| Article | `articles.json` + `articles/*.md` | evidenceIds; JSON body = MD |
| Evidence | `evidence.json` | supports: entitás vagy entitás.mező |

## Publikus vs. kutatási megjegyzés

- `notes`: rövid, publikálható magyarázat
- `researchNotes`: belső / katalóguson kívüli állítások — a felület nem mutatja tényként

## Nem állított kapcsolatok

- `sells_brand` ≠ hivatalos márkakereskedő
- márkakínálat ≠ modellkészlet ≠ kipróbálhatóság
- szervezeti szervizoldal ≠ telephelyi szerviz
