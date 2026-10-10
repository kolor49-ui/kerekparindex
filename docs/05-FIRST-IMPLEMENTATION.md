# Első Cursor-feladat és átvétel

## Cél

Az elfogadott C · ORBIT főoldal helyben futtatható, karbantartható integrációja, vizuális egyezéssel. Első körben nem kell a teljes országos adatbázist és minden aloldalt megépíteni.

## Munkamenet

1. Olvasd el az indulócsomagot és a célrepository meglévő utasításait. Vizsgáld meg, van-e már alkalmazás és használt technológia.
2. Meglévő projekt esetén annak eszközeit használd. Üres projekt esetén az első körhöz a build nélküli HTML/CSS/JS is megfelelő; ne telepíts szükségtelen backend- vagy keretrendszer-függőségeket. Dokumentáld a választást és az indítást.
3. Tartsd érintetlenül a `reference/` mappát. A megvalósítás külön fájlokba kerüljön.
4. Emeld át a C-változatot. Lehetséges komponensek: fejléc, hero, márkasáv, kereső, kategóriák, e-bike magyarázó, tartalmi belépők, helykereső-belépő, lábléc.
5. Távolítsd el a felső A/B/C választót. A referencia főüzenetét, arányait és stílusát őrizd meg.
6. A kategória-, márka- és szerkesztési minták kerüljenek külön adatszerkezetbe. Maradjon világos, hogy nem élő adatbázis.
7. Ellenőrizd a kattintható elemeket. Ha egy aloldal még nem létezik, maradjon korrekt, bezárható prototípus-tájékoztató; ne vezessen 404-re és ne ígérjen elvégzett keresést.
8. Futtasd a szükséges projektellenőrzéseket és tényleges böngészős vizsgálatot. Készíts összehasonlítható screenshotokat és rövid eredményjelentést.

## Kötelező működés az első körben

- A navigáció a megfelelő főoldali szakaszhoz visz.
- A márkák és kategóriák kattinthatók; a cél vagy a prototípusállapot világos.
- A kereső az elérhető helyi márka-/kategóriamintákon működik, kis/nagybetű és ékezet kezeléssel.
- Üres találat esetén van érthető üzenet; törölt kereséssel minden elem visszaállítható.
- A Wh/Nm/km fülek tartalma vált, az aktív állapot és az akadálymentes jelölés együtt frissül.
- A dialógusok billentyűzettel kezelhetők, Escape-re bezárhatók; bezárás után a fókusz visszatér a nyitóelemre.
- Mobilon nincs vízszintes oldaltúlcsordulás, olvashatatlan cím vagy egymásra csúszó kattintható elem.
- Csökkentett mozgás beállítása tiszteletben marad.

## Vizuális ellenőrzés

Vizsgálandó szélességek: 360, 390, 768, 1024, 1440 px. A mellékelt screenshot mérete külön ellenőrizhető; az összehasonlítást azonos nézetmérettel végezd. A referencia és az implementáció készüljön ugyanazzal a böngészővel és betűkörnyezettel is összevetésre.

Figyelj: színek, betűcsalád és súly, címtörések, hero arányai, átlós formák, illusztráció helyzete, navigáció, gombméretek, márkasáv, mobilos sorrend. A felső demo-sáv elhagyásának eltolását külön kezeld.

A korábbi HTML mobilos CSS-e nem egyenlő igazolt mobilos minőséggel. Ha javítás kell, az elfogadott vizuális irányon belül végezd; a jelentésben szerepeljen a hiba és a konkrét változás. Ha nem tudsz böngészőt futtatni, jelöld a vizsgálatot elmaradtként, ne írd, hogy megfelelt.

## Alaptechnika

Magyar `lang`, értelmes címsorhierarchia, egyetlen fő H1, szemantikus gombok és linkek, látható fókusz. Helyi/prototípus build ne kerüljön véletlenül indexelhető éles publikációba. Valódi domainre mutató canonical, sitemap és structured data az éles URL-ek és valós tartalom ismeretében készüljön; ne legyen fiktív Product/Offer értékelés vagy ár.

## Első körön kívül

Éles publikálás és domainkötés, scraping, partneri API-k, fizetés, kosár, belépés, felhasználói fiók, admin/CMS, AI-chatbot, teljes termékkatalógus. Az „AI éve” vizuális modernségi kérés volt; nem jóváhagyott chatbot-funkció.

## Átadáskor kérem

- Futtatási parancs és lokális elérési cím.
- Módosított/létrehozott fájlok és rövid indoklás.
- Ellenőrzések tényleges eredménye, screenshotok nézetmérettel.
- Vizuális eltérések listája, ha vannak.
- Kész, demonstrációs és még hiányzó funkciók külön felsorolva.
- Következő javasolt feladat röviden, önkényes scope-bővítés nélkül.
