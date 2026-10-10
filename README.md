# KERÉKPÁRINDEX — Cursor indulócsomag v1

Átadás dátuma: 2026-10-09. Domain: kerekparindex.hu (a tulajdonos közlése alapján regisztrálva).

## Mi van a csomagban?

- `reference/kerekparindex-v2-c.html`: az elfogadott C · ORBIT látványterv, változatlan forrás.
- `reference/orbit-elfogadott-desktop.png`: a felhasználó által elfogadott nyitóképernyő.
- `docs/01-PROJECT-BRIEF.md`: cél, közönség, prioritások, határok.
- `docs/02-SITE-AND-CONTENT.md`: oldalak és tartalmi rendszer.
- `docs/03-DESIGN-BASELINE.md`: vizuális alap és megőrzendő elemek.
- `docs/04-DATA-AND-EDITORIAL.md`: javasolt adatmodell és forráskezelés.
- `docs/05-FIRST-IMPLEMENTATION.md`: első megvalósítási feladat és átvételi feltételek.
- `PROJECT-DECISIONS.md`: elfogadott döntések és még nyitott kérdések.
- `CURSOR-START.md`: bemásolható induló utasítás.
- `MANIFEST.json`: fájllista és SHA-256 ellenőrzőösszegek.

## Indítás

1. Csomagold ki egy külön KERÉKPÁRINDEX projektmappába, majd nyisd meg Cursorban.
2. Add meg a `CURSOR-START.md` tartalmát a Cursor agentnek.
3. A referenciát közvetlenül Chrome-ban is megnyithatod.

Az HTML önálló, nincs külső betű-, kép- vagy scriptfüggősége. Az A/B/C változatváltó A és B linkjei ebben az egyváltozatos átadócsomagban szándékosan nem rendelkeznek célfájllal; a referencia eredetiségét megőriztük. A megvalósításból a teljes változatválasztó sáv eltávolítandó.

## Átadási állapot

Ez elfogadott vizuális alap és induló specifikáció, nem kész éles rendszer. A HTML kategória- és márkakeresése, paraméterfülei és tájékoztató dialógusai demonstrációk. Nincs élő termék-, akció-, készlet- vagy üzletadatbázis. A márkanevek szöveges helyőrzők, a kerékpár stilizált SVG-illusztráció.

A JavaScript szintaxisa és a belső hivatkozások ellenőrzöttek. A mellékelt képernyőkép a felhasználó asztali megjelenítését dokumentálja; teljes, több méreten futó böngészős QA még nem történt. Publikálás, DNS-beállítás, tárhely és repository létrehozása nem része ennek az átadásnak.
