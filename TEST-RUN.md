# Ellenőrzési tesztfuttatás — ORBIT v1 UX/a11y

Dátum: 2026-10-09  
Előfeltétel: a főoldal helyi szerveren fut (`python3 -m http.server 8765` → http://127.0.0.1:8765/)  
Eszköz: Chrome (`/Applications/Google Chrome.app/...`) + `puppeteer-core@23.11.1` (ideiglenes telepítés temp könyvtárban; **nem** része a projektnek)

## Parancs

```bash
# 1) Szerver (ha még nem fut)
cd /Users/macbookair/Desktop/kerekparindex
python3 -m http.server 8765

# 2) Smoke (másik terminálban) — puppeteer-core temp dir-ben
TMP=$(mktemp -d)
cd "$TMP"
npm init -y && npm install --no-fund --no-audit puppeteer-core@23.11.1
# smoke.mjs: H1 geometria (320–390), nav scroll hint, tab roles + ArrowRight,
# kereső elektromos + clear, CUBE dialog Escape fókusz, desktop H1 ≥ 50px
node smoke.mjs > /Users/macbookair/Desktop/kerekparindex/TEST-RUN-RESULT.json
rm -rf "$TMP"
```

**H1 mérés:** `Range` a teljes „Magyarországon.” szövegre + a pont (`period`) `getClientRects()`; limit = `min(hero.right, innerWidth) - 2`. A szó és a pont jobb széle egyaránt ≤ limit; nincs page horizontal overflow.

Screenshotok (Chrome headless, overwrite; cache disabled):

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=/Users/macbookair/Desktop/kerekparindex/screenshots
TS=$(date +%s)
for size in "320x800:320" "360x800:360" "375x812:375" "390x844:390" \
            "768x1024:768" "1024x900:1024" "1440x900:1440"; do
  dim="${size%%:*}"; name="${size##*:}"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
    --disk-cache-size=1 --media-cache-size=1 --disable-application-cache \
    --window-size="${dim%x*},${dim#*x}" \
    --screenshot="$OUT/impl-${name}.png" \
    "http://127.0.0.1:8765/?cb=${TS}-${name}"
done
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1440,900 \
  --screenshot="$OUT/ref-1440.png" \
  "http://127.0.0.1:8765/reference/kerekparindex-v2-c.html"
```

## Eredmény

Kilépési kód: `0` · `pass: true`

### Összefoglaló asszerciók

| Terület | Eredmény |
| --- | --- |
| H1 geometria 320 / 360 / 375 / 390 | PASS (last char „Magyarországon.” nem vágott; nincs page overflow) |
| Nav scroll hint (5 link, `.nav-scroll`, fade / `is-scrollable`) | PASS |
| Metrics tab roles + ArrowRight + nincs `aria-pressed` | PASS |
| Kereső „elektromos” + clear; CUBE Escape fókusz | PASS |
| Desktop 1440 H1 `font-size` ≥ 50px | PASS (`82.08px`) |

### H1 CSS (végleges)

- `max-width: 740px`: `clamp(26px, 7.2vw, 42px)`, `letter-spacing: -1.1px`
- `max-width: 390px`: `clamp(24px, 6.8vw, 34px)`, `letter-spacing: -0.9px`

### JSON összefoglaló

```json
{
  "pass": true,
  "summary": {
    "h1Geometry": {
      "320": {
        "pass": true,
        "h1FontSize": "24px",
        "letterSpacing": "-0.9px",
        "wordRight": 224.890625,
        "lastCharRight": 224.890625,
        "limit": 300,
        "heroRight": 302,
        "includesFullWord": true
      },
      "360": {
        "pass": true,
        "h1FontSize": "24.48px",
        "letterSpacing": "-0.9px",
        "wordRight": 228.828125,
        "lastCharRight": 228.828125,
        "limit": 340,
        "heroRight": 342,
        "includesFullWord": true
      },
      "375": {
        "pass": true,
        "h1FontSize": "25.5px",
        "letterSpacing": "-0.9px",
        "wordRight": 237.21875,
        "lastCharRight": 237.21875,
        "limit": 355,
        "heroRight": 357,
        "includesFullWord": true
      },
      "390": {
        "pass": true,
        "h1FontSize": "26.52px",
        "letterSpacing": "-0.9px",
        "wordRight": 245.609375,
        "lastCharRight": 245.609375,
        "limit": 370,
        "heroRight": 372,
        "includesFullWord": true
      }
    },
    "nav": {
      "320": { "pass": true, "hasFade": true, "fadeWidth": 36 },
      "360": { "pass": true, "hasFade": true, "fadeWidth": 36 },
      "375": { "pass": true, "hasFade": true, "fadeWidth": 36 },
      "390": { "pass": true, "hasFade": true, "fadeWidth": 36 }
    },
    "metricsTabs": {
      "320": { "pass": true },
      "360": { "pass": true },
      "375": { "pass": true },
      "390": { "pass": true }
    },
    "searchAndDialog": { "pass": true },
    "desktopH1FontSize": { "pass": true, "fontSizePx": 82.08 }
  }
}
```

Teljes nyers eredmény: `TEST-RUN-RESULT.json`
