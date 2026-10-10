# Adatok és szerkesztési alapelvek

Az alábbi modell induló javaslat, nem kész adatbázisséma. Első körben elegendő strukturált helyi adat; a termelési adatbázis kiválasztása külön technikai döntés.

| Entitás | Lényeges mezők, kapcsolatok |
| --- | --- |
| Brand | id, név, slug, termékkörök, hivatalos webhely, leírás, médiaforrás |
| Organization | id, cégnév, szerepek: gyártó/importőr/kereskedő/szolgáltató |
| Location | id, organizationId, üzlet/műhely neve, cím, koordináták, nyitvatartás, kapcsolatok |
| Service | szolgáltatástípus, locationId, márka/rendszer, igazolt jogosultság és forrás |
| Product | id, brandId, terméktípus, modellsorozat, modellév, név, specifikációk |
| Variant | productId, méret, szín, cikkszám és azonosítók, ha ellenőrzöttek |
| Offer | variantId vagy egyértelmű productId, kereskedő, cél-URL, pénznem, ár, érvényesség, ellenőrzési idő |
| Article | cím, slug, típus, saját tartalom, források, ellenőrzési idő, kapcsolt márkák és termékek |
| Evidence | forrás-URL, mező/állítás, hozzáférés dátuma, ellenőrzési státusz |

A céget és a telephelyet külön kezeld. Egy termék több kereskedői ajánlathoz kapcsolódhat. Az azonos név nem bizonyít azonos modellévet, méretet vagy felszereltséget. A „hivatalos kereskedő” nem azonos a „márkát áruló üzlet” jelöléssel.

## Adatminőség

- Ismeretlen adat legyen hiányzó/null vagy „nem ismert”, ne kitalált érték.
- Termékleírásból ne következtess aktuális készletre vagy kipróbálhatóságra.
- Ajánlatnál legyen látható a kereskedő, az ellenőrzés ideje és az ismert érvényesség; lejárt ajánlat ne legyen aktívként feltüntetve.
- Csak hitelesen ismert összehasonlítási alapból számolj kedvezményt. Ne találj ki áthúzott árat.
- Készletet és konkrét méretet csak adatforráshoz és frissítési időhöz kötve mutass.
- Kompatibilitást ne állíts márkanév alapján; a pontos modell és rendszer ellenőrzése szükséges.
- Mintaadat helyi prototípusban legyen egyértelműen jelölve; élő oldalon ne látszódjon valódi ajánlatnak.

## Tartalom és média

Saját szövegezés, ellenőrizhető elsődleges források. A gyártói adatokat különítsd el a szerkesztői értelmezéstől. Bemutató nem nevezhető saját tesztnek tényleges kipróbálás nélkül. Fotó, logó és külső szöveg felhasználási feltételeit ellenőrizni kell. Szponzorált megjelenés legyen elkülöníthető a szerkesztői tartalomtól.

## Adatgyűjtési irány

Későbbi munka: márkák és hazai képviseletek → partnerhálózatok; ezzel párhuzamosan településenként üzletek és szervizek. Deduplikálás és forrásellenőrzés szükséges. Az élő ár/készlet országos teljességét nyilvános oldalak alkalmi átnézése nem garantálja; kereskedői feed/API külön integrációs feladat.
