# Oldalszerkezet és tartalom

## Főoldal — az elfogadott HTML sorrendje

1. Fejléc: KERÉKPÁRINDEX, Márkák, Minden ami kerékpár, Elektromos, Üzletek és szervizek, Akciók, kereső.
2. ORBIT hero: országos főüzenet, leírás, „Fedezd fel a kínálatot”, e-bike belépő.
3. Márkasáv: ismert márkák hangsúlyos bemutatása.
4. Kereső.
5. Hat fő kategória: Kerékpárok, Elektromos, Alkatrészek, Felszerelések, Üzletek, Szervizek.
6. Kiemelt e-bike blokk: Wh / Nm / km magyarázó és tartalmi belépők.
7. Akciók, újdonságok és bemutatók, ár–érték összehasonlítások.
8. Üzlet- és szervizkereső belépő.
9. Lábléc.

A képernyőképen a márkasáv a hajtás közelében kezdődik; ne állítsd ellenőrzés nélkül, hogy minden logó minden képernyőn hajtás fölött van. A márkák még korábbi elhelyezését külön vizuális javaslatként lehet bemutatni, az elfogadott hero önkényes átméretezése nélkül.

## Tervezett oldaltípusok és javasolt útvonalak

| Útvonal | Feladat |
| --- | --- |
| `/` | Főoldal |
| `/markak` és `/markak/[slug]` | Márkafelfedezés, összekötött bemutatók, termékkörök, üzletek, akciók |
| `/kerekparok` | Kerékpártípusok, márkák, kínálat |
| `/elektromos-kerekparok` | Önálló e-bike tartalmi központ |
| `/alkatreszek` | Alkatrészkategóriák és kapcsolódó tartalmak |
| `/felszerelesek` | Sisak, lakat, világítás, táska, ruházat, szállítás, ápolás stb. |
| `/uzletek` és `/szervizek` | Hely és szolgáltatás szerinti keresés |
| `/akciok` | Ellenőrzött, kereskedőhöz kötött ajánlatok |
| `/ujdonsagok`, `/bemutatok`, `/osszehasonlitasok` | Szerkesztett tartalom |
| `/vasarlasi-segitseg` | Másodlagos választási útmutatók |

Ez célstruktúra, nem utasítás az összes oldal egyidejű elkészítésére.

## Márkaoldal

Márkanév és jóváhagyott arculati eszközök; rövid saját bemutatás; jelen lévő termékkörök; bemutatók és összehasonlítások; igazolt hazai vásárlási pontok; akciók. A márka elérhetősége, hivatalos képviselete és az egyes üzletek státusza külön ellenőrizendő.

## Elektromoskerékpár-központ

Bemutatók; ár–érték összehasonlítások; motor és nyomaték; akkumulátor és kapacitás; hatótáv körülményei; tömeg; felszereltség; kipróbálás; karbantartás és szervizháttér; újdonságok és akciók.

Minden paraméternél: mit jelent → miért számít → mit érez belőle a használó → mivel együtt érdemes nézni. Kerülendő az a benyomás, hogy egyetlen nagyobb szám automatikusan jobb kerékpárt jelent.

## Kategóriázás

A kerékpártípus (városi, trekking, MTB, országúti, gravel, gyermek, cargo, összecsukható stb.) és az elektromos rásegítés külön tulajdonság. Egy elektromos trekking mindkét releváns útvonalon elérhető lehet, egyetlen közös rekordból.
