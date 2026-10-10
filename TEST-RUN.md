# Ellenőrzési tesztfuttatás — ORBIT Compact

Dátum: 2026-10-10  
Előfeltétel: a főoldal helyi szerveren fut (`python3 -m http.server 8765` → http://127.0.0.1:8765/)  
Eszköz: Chrome (`/Applications/Google Chrome.app/...`) + `puppeteer-core@23.11.1` (ideiglenes telepítés temp könyvtárban; **nem** része a projektnek)  
Éles deploy: **nem** történt (Vercel / production elkerülve).

## Parancs

```bash
# 1) Szerver (ha még nem fut)
cd /Users/macbookair/Desktop/kerekparindex
python3 -m http.server 8765

# 2) Smoke (másik terminálban) — puppeteer-core temp dir-ben
TMP=$(mktemp -d)
cd "$TMP"
npm init -y && npm install --no-fund --no-audit puppeteer-core@23.11.1
cp /Users/macbookair/Desktop/kerekparindex/scripts/smoke-compact.mjs ./smoke-compact.mjs
PROJECT_ROOT=/Users/macbookair/Desktop/kerekparindex node smoke-compact.mjs \
  > /Users/macbookair/Desktop/kerekparindex/TEST-RUN-RESULT.json
rm -rf "$TMP"
```

A smoke script (`scripts/smoke-compact.mjs`):

- Viewportok: 360×900, 390×900, 768×1100, 1024×900, 1440×900
- Full-page screenshotok: `screenshots/compact-{360,390,768,1024,1440}.png`
- Szekció-sorrend id szerint: `markak` → `search` → `felfedezes` → `aktualis` → `elektromos` → `helyek`
- H1 tartalmazza a teljes „Magyarországon.” szót; a szó `Range` client rect jobb széle &lt; `innerWidth - 2`
- Mobil 360/390: `menu-toggle` látható; kattintás megnyitja a navot (`open`, `aria-expanded=true`); Escape bezár; 5 nav link
- Kereső: `elektromos` → `visibleCats` tartalmazza `Elektromos`; clear visszaállít
- Metrics: `tab` / `tablist` / `tabpanel`; nincs `aria-pressed`; ArrowRight → `nm`; explanation frissül
- Dialog: CUBE → Escape → fókusz vissza a CUBE gombra
- Desktop 1440: hero art nem `display:none`; H1 ~36px (kompakt, nem a régi ~80px)

## Eredmény

Kilépési kód: `0` · `pass: true`

### H1 font-size viewportonként

| Viewport | H1 font-size |
| --- | --- |
| 360 | 25px |
| 390 | 25px |
| 768 | 30px |
| 1024 | 30px |
| 1440 | 36px |

### Összefoglaló asszerciók

| Terület | Eredmény |
| --- | --- |
| Section order (mind az 5 viewport) | PASS |
| H1 „Magyarországon.” + viewport clamp | PASS |
| Mobile nav 360 / 390 | PASS |
| Search elektromos + clear | PASS |
| Metrics tabs + ArrowRight → nm | PASS |
| CUBE dialog Escape fókusz | PASS |
| Desktop 1440 hero art + compact H1 (36px) | PASS |
| Live deploy elkerülve | yes |

### JSON összefoglaló

```json
{
  "pass": true,
  "summary": {
    "pass": true,
    "h1FontSizes": {
      "360": "25px",
      "390": "25px",
      "768": "30px",
      "1024": "30px",
      "1440": "36px"
    },
    "sectionOrderOk": true,
    "mobileNavOk": true,
    "searchOk": true,
    "metricsOk": true,
    "dialogOk": true,
    "desktopOk": true,
    "liveDeployAvoided": true
  }
}
```

Teljes nyers eredmény: `TEST-RUN-RESULT.json`
