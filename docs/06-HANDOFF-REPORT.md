# Átadási jelentés — első főoldali integráció

Dátum: 2026-10-09  
Alap: C · ORBIT (`reference/kerekparindex-v2-c.html`)

## Futtatás

```bash
cd /Users/macbookair/Desktop/kerekparindex
python3 -m http.server 8765
```

Lokális cím: [http://127.0.0.1:8765/](http://127.0.0.1:8765/)

Referencia (változatlan): [http://127.0.0.1:8765/reference/kerekparindex-v2-c.html](http://127.0.0.1:8765/reference/kerekparindex-v2-c.html)

**Technológiai választás:** üres mappa → build nélküli HTML/CSS/JS. Nincs framework, backend vagy npm-függőség. Indoklás: `docs/05-FIRST-IMPLEMENTATION.md` szerint az első körhöz ez megfelelő.

## Létrehozott / módosított fájlok

| Fájl | Indok |
| --- | --- |
| `index.html` | Főoldal: C · ORBIT tartalom, A/B/C demo-sáv nélkül |
| `css/main.css` | ORBIT stílusok; A/B változat-CSS eltávolítva; C-szabályok alapértelmezetté téve |
| `js/main.js` | Kereső, Wh/Nm/km, dialógusok, fókusz-visszaállítás |
| `data/sample.js` | Márka-/kategória-/tartalmi mintaadatok; nem élő DB |
| `screenshots/` | Böngészős képernyőképek nézetméretenként |
| `docs/06-HANDOFF-REPORT.md` | Ez a jelentés |

A `reference/` mappa érintetlen.

## Ellenőrzések

### Szerver
- `index.html`, CSS, JS, mintaadat, referencia: HTTP 200.

### Interakciók (Chrome headless, 1440×900 + 360×800)
Tényleges eredmény:
- demo-sáv nincs (`noDemo: true`)
- keresés „elektromos” → 1 találat (Elektromos); törlés után 0 rejtett elem
- Nm fül aktív + `aria-pressed`; magyarázó cím frissül
- CUBE dialógus megnyílik; Escape után fókusz vissza a CUBE gombra
- egy H1, `lang=hu`
- 360 px: nincs vízszintes oldaltúlcsordulás (`mobileOverflowX: false`)
- `prefers-reduced-motion` CSS megőrizve
- `noindex` a helyi prototípuson

### Screenshotok
Chrome headless (`--headless=new`), fájlok: `screenshots/impl-{360,390,768,1024,1440}.png`, `screenshots/ref-1440.png`.

Megjegyzés: a headless Chrome betűrenderelése eltérhet a felhasználó asztali Chrome-jától; a mellékelt `reference/orbit-elfogadott-desktop.png` a jóváhagyott asztali bizonyíték.

## Vizuális eltérések a referenciához képest

1. **Felső A/B/C demo-sáv eltávolítva** — szándékos; a tartalom ~30–40 px-szel feljebb kerül.
2. **Lábléc szövege** — a „C / ORBIT · változatválasztás” leírás helyett mintaadat-jelölés (spec szerint).
3. **Fájlszerkezet** — inline CSS/JS szétválasztva; megjelenés a C-szabályokkal egyezőnek szánt.
4. Egyéb szándékos designváltoztatás nincs.

## Funkcióállapot

**Kész**
- Főoldal vizuális integráció (ORBIT)
- Navigáció, kereső, e-bike magyarázó, prototípus-dialógusok
- Reszponzív CSS (1100 / 740 px töréspontok)

**Demonstráció (nem élő adat)**
- Márkanevek helyőrzők
- Kategória- és tartalmi belépők dialógusokkal
- Üzlet/szerviz belépő dialógus

**Hiányzik (szándékosan, első körön kívül)**
- Aloldalak (`/markak`, `/uzletek`, …)
- Élő adatbázis, CMS, deploy, domain
- Hivatalos logók / termékfotók

## Következő javasolt feladat

Márkalista-oldal (`/markak`) szerkezeti váz a meglévő ORBIT stílussal és a `data/sample.js` márkamintáival — még mindig helyi mintaadattal, partnerség- vagy árállítás nélkül.
