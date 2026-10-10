# KERÉKPÁRINDEX — tartalmi próbakör v2

**Dátum:** 2026-10-10  
**Vizuális alap:** ORBIT Compact  
**Csomag:** `kerekparindex-content-pilot-v2`

## Darabszámok

| Elem | Kész | Megjegyzés |
| --- | --- | --- |
| Márka | 10 | 9× ellenőrzött, Scott előkészített |
| Telephely | 103 | brandLinks + evidenceIds; szolgáltatás szerepenként bizonyíték |
| E-bike modellváltozat | 12 | forrás supports + pageTitle |
| Alapmagyarázó | 6 | konkrét szakmai források |
| Összehasonlítás | 3 | trekking / e-MTB / városi komfort |

## Ellenőrzés

```bash
python3 scripts/verify-content-pilot.py
```

## Mit NEM állít a csomag

- Élő ár / készlet / kipróbálhatóság országos adatbázisa
- Hivatalos márkakereskedő státusz bizonyíték nélkül
- Modell–üzlet kapcsolat konkrét forrás nélkül
- Saját menetpróba, mért hatótáv, abszolút győztes

Részletek: `STATUS-SUMMARY.md`, `schema.md`, `meta.json`.
