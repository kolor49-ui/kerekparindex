/**
 * Helyi prototípus-mintaadatok — ORBIT Compact.
 * Nem élő adatbázis, nem igazolt partnerség vagy ajánlat.
 */
window.KEREKPARINDEX_SAMPLE = {
  notice:
    "Helyi prototípus: a megjelenő márkák, kategóriák és tartalmi belépők mintaadatok. Élő ajánlat- és üzletadatbázis még nincs.",
  brands: [
    { id: "cube", name: "CUBE" },
    { id: "trek", name: "TREK" },
    { id: "giant", name: "GIANT" },
    { id: "specialized", name: "SPECIALIZED" },
    { id: "merida", name: "MERIDA" },
    { id: "scott", name: "SCOTT" },
  ],
  categories: [
    { id: "kerekparok", name: "Kerékpárok", subtitle: "Típusok és márkák" },
    {
      id: "elektromos",
      name: "Elektromos",
      subtitle: "Modellek és magyarázók",
      scrollTo: "elektromos",
    },
    { id: "alkatreszek", name: "Alkatrészek", subtitle: "A hajtástól a fékig" },
    { id: "felszerelesek", name: "Felszerelések", subtitle: "Minden az útra" },
    { id: "uzletek", name: "Üzletek", subtitle: "Vásárlás és kipróbálás" },
    { id: "szervizek", name: "Szervizek", subtitle: "Karbantartás és javítás" },
  ],
  metrics: {
    wh: {
      title: "Az energia, amit magaddal viszel.",
      body: "A wattóra az akkumulátorban tárolható energia mennyiségét jelzi. Több Wh nagyobb energiatartalékot jelent; a hatótávhoz a terepet, a terhelést és a rásegítés mértékét is nézni kell.",
    },
    nm: {
      title: "A rásegítés egyik fontos jellemzője.",
      body: "A newtonméter a motor forgatónyomatékának mértékegysége. Emelkedőn vagy nagyobb terhelésnél különösen érdekes, de a menetérzetet a vezérlés és az áttétel is alakítja.",
    },
    km: {
      title: "Egy szám, sok feltétellel.",
      body: "A hatótáv függ a tereptől, a terheléstől, az időjárástól és a választott rásegítéstől. A megadott kilométerérték mellett mindig keresd a mérési körülményeket is.",
    },
  },
  editorialBodies: {
    "Jó vételt keresel?":
      "<p>Itt jelenhetnek majd meg a kereskedők ellenőrzött ajánlatai, érvényességgel és forráslinkkel. Ebben a látványtervben még nincs élő akciós kínálat.</p>",
    "500 vagy 750 Wh?":
      "<p>A Wh az akkumulátorban tárolható energiát jelzi. A nagyobb kapacitás több energiatartalékot ad, de a hatótávot a terep, a terhelés, az időjárás és a rásegítés is alakítja.</p><p>Választásnál a teljes kerékpár tömegét, a töltést és az akkumulátor cserélhetőségét is érdemes megnézni.</p>",
    "Mitől drágább egy e-bike?":
      "<p>Hasonlítsd össze a hajtásrendszert, az akkumulátort, a fékeket, a váltót, a vázat és a felszereltséget. Egyetlen paraméter nem írja le az egész kerékpárt.</p><p>A szervizháttér és a használati igényeid ugyanúgy részei a döntésnek.</p>",
    "E-bike-bemutatók":
      "<p>Itt önálló szerkesztett tartalmak jelennek majd meg: érthető magyarázatokkal, ellenőrzött forrásokkal és a kapcsolódó kereskedők elérhetőségével.</p><p>Ez egy tartalmi belépő látványterve, nem élő ajánlat vagy megjelent teszt.</p>",
    "E-bike-összehasonlítások":
      "<p>Itt önálló szerkesztett tartalmak jelennek majd meg: érthető magyarázatokkal, ellenőrzött forrásokkal és a kapcsolódó kereskedők elérhetőségével.</p><p>Ez egy tartalmi belépő látványterve, nem élő ajánlat vagy megjelent teszt.</p>",
    "Elektromoskerékpár-akciók":
      "<p>Itt jelenhetnek majd meg a kereskedők ellenőrzött ajánlatai, érvényességgel és forráslinkkel. Ebben a látványtervben még nincs élő akciós kínálat.</p>",
  },
  dialogPaths: [
    "Modellek és bemutatók",
    "Alkatrészek és felszerelések",
    "Hazai kereskedők",
    "Összehasonlítások",
    "Akciók",
  ],
  localServices: ["Vásárlás", "Kipróbálás", "Általános szerviz", "E-bike-szerviz"],
};
