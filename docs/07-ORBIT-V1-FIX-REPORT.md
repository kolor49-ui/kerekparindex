# ORBIT v1 — célzott UX / a11y javítások

Dátum: 2026-10-09  
Projekt: KERÉKPÁRINDEX C · ORBIT (helyi prototípus)  
Kapcsolódó: `docs/06-HANDOFF-REPORT.md`

## Mi változott (3 javítás)

1. **Mobil H1 méret / tracking** — `css/main.css`:
   - `@media (max-width: 740px)`: `clamp(26px, 7.2vw, 42px)`, `letter-spacing: -1.1px`
   - `@media (max-width: 390px)`: `clamp(24px, 6.8vw, 34px)`, `letter-spacing: -0.9px`
   - padding és overflow, hogy a „Magyarországon.” teljesen látszódjon 320–390 px között.
2. **Mobil nav scroll hint** — `.nav-scroll` fade (`::after`), vékony accent scrollbar, JS `is-scrollable` / `is-end` osztályok (`js/main.js`).
3. **E-bike metrics tab pattern** — `role="tablist" / "tab" / "tabpanel"`, `aria-selected` (nincs `aria-pressed`), billentyűzet: ArrowRight/Left, Home/End.

## DESIGN LOCK

- ORBIT vizuális nyelv megőrizve (színek, tipográfia, layout, demo-sáv nélkül).
- Desktop hero H1 nagy marad (1440-en mért `font-size`: **82.08px**, ≥ 50px).
- Referencia HTML (`reference/kerekparindex-v2-c.html`) érintetlen; a javítások csak az implementációban.
- Nincs új brand szín, nincs layout újratervezés — csak mobil olvashatóság + a11y.

## Viewport lista (screenshotok)

| Fájl | Méret |
| --- | --- |
| `screenshots/impl-320.png` | 320×800 |
| `screenshots/impl-360.png` | 360×800 |
| `screenshots/impl-375.png` | 375×812 |
| `screenshots/impl-390.png` | 390×844 |
| `screenshots/impl-768.png` | 768×1024 |
| `screenshots/impl-1024.png` | 1024×900 |
| `screenshots/impl-1440.png` | 1440×900 |
| `screenshots/ref-1440.png` | 1440×900 (referencia HTML) |

## Teszt eredmények összefoglaló

Forrás: `TEST-RUN.md` + `TEST-RUN-RESULT.json` (2026-10-09), `pass: true`.

**H1 mérés:** `Range` a teljes „Magyarországon.” + period rect; limit = `min(hero.right, innerWidth) - 2`.

| Szélesség | H1 font-size | letter-spacing | lastCharRight | wordRight | limit | Eredmény |
| --- | --- | --- | --- | --- | --- | --- |
| 320 | 24px | -0.9px | 224.890625 | 224.890625 | 300 | PASS |
| 360 | 24.48px | -0.9px | 228.828125 | 228.828125 | 340 | PASS |
| 375 | 25.5px | -0.9px | 237.21875 | 237.21875 | 355 | PASS |
| 390 | 26.52px | -0.9px | 245.609375 | 245.609375 | 370 | PASS |

| Asszerció | 320 | 360 | 375 | 390 | 1440 |
| --- | --- | --- | --- | --- | --- |
| H1 / „Magyarországon.” nem vágott | PASS | PASS | PASS | PASS | — |
| Nincs page horizontal overflow | PASS | PASS | PASS | PASS | — |
| Nav 5 link + scroll hint | PASS | PASS | PASS | PASS | — |
| Metrics tabs + ArrowRight | PASS | PASS | PASS | PASS | PASS |
| Desktop H1 ≥ 50px | — | — | — | — | PASS (82.08px) |
| Kereső + CUBE Escape fókusz | — | — | — | PASS | — |

## Érintett fájlok (javítások)

- `css/main.css` — mobil H1 + nav scroll hint stílusok
- `js/main.js` — tab keyboard / `aria-selected`; nav scroll hint osztályok
- `index.html` — tablist / tab / tabpanel markup
- `screenshots/*` — frissített headless képernyőképek
- `TEST-RUN.md`, `TEST-RUN-RESULT.json` — ellenőrzési futás
- `docs/07-ORBIT-V1-FIX-REPORT.md` — ez a jelentés

## Következő lépés (kívül e körön)

Aloldalak (`/markak` stb.) — **nem** indult ebben a csomagban.
