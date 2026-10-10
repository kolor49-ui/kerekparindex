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
