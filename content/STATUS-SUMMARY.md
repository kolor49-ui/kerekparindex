# Tartalmi próbakör v2 — hiányok, konfliktusok, státuszok

Dátum: 2026-10-10  
Csomag: `kerekparindex-content-pilot-v2`

## Státuszjelentés (egységes)

| Érték | Jelentés |
| --- | --- |
| ellenőrzött | Forrással igazolt mezők; feloldatlan ellentmondás nem tényként jelenik meg |
| előkészített | Részleges forrás (Scott) vagy archivált gyártói oldal |
| hiányos | Kritikus adat hiányzik a rekord publikálásához |

Adatjelzők: `archivált` · `ellentmondás` · `hiányzó_adat`

## Darabszámok

| Entitás | Publikálható | Megjegyzés |
| --- | --- | --- |
| Márkák | 10 | 9 ellenőrzött + Scott előkészített |
| Telephelyek | 101 | Országos bővítés (20→101); brandLinks + evidenceIds |
| Szolgáltatások | telephelyi szerepek | Rekord BP/Győr szerviz továbbra is visszatartva |
| Modellváltozatok | 12 | MERIDA archived → előkészített |
| Magyarázók | 6 | Konkrét Bosch / gyártói forrásokkal |
| Összehasonlítások | 3 | Városi komfort (átnevezve), trekking, e-MTB |

## Javítások ebben a körben

1. Márka–üzlet `brandLinks` a `_research` brandClaims-ből, stabil `brandId`-vel; katalóguson kívüli márkák `researchNotes`-ban.
2. Telephely `evidenceIds`, modell `supports` + `pageTitle`, magyarázó szakmai források.
3. Összehasonlítások: Trek **24,9 kg, akkumulátor nélkül**; mérési feltételek; modellenként előny/kompromisszum; „kompakt városi” → városi / mindennapi komfort; hardtail vs. összteleszkóp magyarázat.
4. Rekord szerviz nem mindkét telephelyen; státusz/flag szétválasztás.
5. Szerkesztői javítás; `null` → „Nincs ellenőrzött adat”; kutatási megjegyzések elkülönítve.
6. UI bekötés Compact dialógusokkal; hiányos részek nem tartják vissza a kész tartalmat.

## Visszatartott

- Rekord Bike telephelyi szerviz (csak szervezeti oldal)
- Modell–üzlet készlet / kipróbálás kapcsolatok (nincs bizonyíték)
- Katalóguson kívüli márkanevek (Bianchi, Marin, …) — nincs stabil brandId
- LOOK pedál-állítás nem sells_brand kerékpármárkaként

## Ellenőrzés

```bash
python3 scripts/verify-content-pilot.py
```
