# Elfogadott vizuális alap — C · ORBIT

Elsődleges forrás: `reference/kerekparindex-v2-c.html`. Vizuális bizonyíték: `reference/orbit-elfogadott-desktop.png`.

## Megőrzendő

- Mélylila alap, korall kiemelések, levendula grafikai formák.
- A hero kompozíciója, nagy tipográfiája, szövege, átlós formái és kerékpár-illusztrációja.
- A fejléc, szójel, navigáció, gombstílus, lekerekítések és térközök aránya.
- Márkasáv és a portáljellegű kategóriabelépők.
- A működő frontend-interakciók szerepe és a reszponzív szabályok kiinduló logikája.

A komponensekre bontás nem jelent engedélyt új designra. CSS-reset, UI-könyvtár vagy alapértelmezett framework-font ne változtassa meg észrevétlenül a megjelenést. SEO-feladat miatt sem változhat a vizuális hierarchia vagy a felirat.

## Forrásból vett alapszínek

| CSS-változó | Érték |
| --- | --- |
| `--bg` | `#191320` |
| `--ink` | `#fff5f1` |
| `--accent` | `#ff966f` |
| `--on` | `#301729` |
| `--muted` | `#c0accb` |
| `--line` | `#46344f` |
| `--surface` | `#2a2034` |
| `--hero` | `#2b1b3c` |
| `--float` | `#2c1c3ddb` |
| `--hover` | `#44314f` |
| `--e-bg` | `#d6b9ff` |
| `--e-ink` | `#302042` |

A `.v-c` szabályok felülírnak egyes alapértékeket: például a hero radiális színátmenetes, az e-bike blokk levendula színátmenetes. A teljes CSS az irányadó; a tokenlista önmagában nem rekonstruálja a designt.

Betűcsalád: `Arial, Helvetica, sans-serif`. Ezt az első integrációban tartsd meg; nincs jóváhagyva új webfont. A forrás hero-címe nagy, tömör, 900-as súlyú, negatív betűközű. Pontos méretek és töréspontok: a referencia CSS-ében (1100 és 740 px, plusz széles képernyős szabályok).

## Eltávolítható demonstrációs elemek a megvalósításban

- A legfelső „C / ORBIT — SZÍN- ÉS HANGULATTERV” és A/B/C választósáv.
- A láblécben a változatválasztási leírás; a szükséges mintaadat-jelölést a helyi prototípusban meg kell tartani.
- Nem használt A/B CSS csak igazolt vizuális egyezés mellett tisztítható.

A referenciafájlt ne szerkeszd. A fenti tisztításból adódó függőleges eltolás elfogadható; egyéb eltéréseket tételesen mutasd be.

## Márkák és képanyag

A CUBE, TREK, GIANT, SPECIALIZED, MERIDA, SCOTT feliratok a prototípusban szöveges helyőrzők. Nem hivatalos logófájlok, nem igazolt partnerségek és nem teljes induló márkalista. Hivatalos arculati eszközökre cserélésük későbbi tartalomfeladat; ne gyárts utánzott logókat. A kerékpár stilizált illusztráció, nem konkrét modell fotója. A most elfogadott képet ne cseréld automatikusan.
