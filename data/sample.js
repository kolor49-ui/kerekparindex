/**
 * Helyi prototípus-mintaadatok.
 * Nem élő adatbázis, nem igazolt partnerség vagy ajánlat.
 */
window.KEREKPARINDEX_SAMPLE = {
  notice:
    "Helyi prototípus: a megjelenő márkák, kategóriák és tartalmi belépők mintaadatok. Élő ajánlat- és üzletadatbázis még nincs.",
  brands: [
    { id: "cube", name: "CUBE", labelStyle: "regular" },
    { id: "trek", name: "TREK", labelStyle: "italic" },
    { id: "giant", name: "GIANT", labelStyle: "tight" },
    { id: "specialized", name: "SPECIALIZED", labelStyle: "italic-tight" },
    { id: "merida", name: "MERIDA", labelStyle: "smaller" },
    { id: "scott", name: "SCOTT", labelStyle: "italic" },
  ],
  categories: [
    {
      id: "kerekparok",
      name: "Kerékpárok",
      num: "01",
      subtitle: "Típusok és márkák",
      scrollTo: null,
    },
    {
      id: "elektromos",
      name: "Elektromos",
      num: "02",
      subtitle: "Modellek és magyarázók",
      scrollTo: "elektromos",
    },
    {
      id: "alkatreszek",
      name: "Alkatrészek",
      num: "03",
      subtitle: "A hajtástól a fékig",
      scrollTo: null,
    },
    {
      id: "felszerelesek",
      name: "Felszerelések",
      num: "04",
      subtitle: "Minden az útra",
      scrollTo: null,
    },
    {
      id: "uzletek",
      name: "Üzletek",
      num: "05",
      subtitle: "Vásárlás és kipróbálás",
      scrollTo: null,
    },
    {
      id: "szervizek",
      name: "Szervizek",
      num: "06",
      subtitle: "Karbantartás és javítás",
      scrollTo: null,
    },
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
  editorial: [
    {
      id: "akciok",
      title: "Akciók és jó vételek",
      eyebrow: "Akciófigyelő",
      heading: "Hol találsz<br>most jó vételt?",
      accent: true,
    },
    {
      id: "ujdonsagok",
      title: "Újdonságok és bemutatók",
      eyebrow: "Újdonságok / bemutatók",
      heading: "Új modellek.<br>Új lehetőségek.",
      accent: false,
    },
    {
      id: "ar-ertek",
      title: "Ár–érték összehasonlítások",
      eyebrow: "Ár–érték / összehasonlítás",
      heading: "Mit kapsz<br>a pénzedért?",
      accent: false,
    },
  ],
  eBikeEditorial: [
    { id: "ebike-bemutatok", title: "E-bike-bemutatók", label: "Bemutatók ↗" },
    {
      id: "ebike-osszehasonlitasok",
      title: "E-bike-összehasonlítások",
      label: "Összehasonlítások ↗",
    },
    {
      id: "ebike-akciok",
      title: "Elektromoskerékpár-akciók",
      label: "Akciók ↗",
    },
  ],
  dialogPaths: [
    "Modellek és bemutatók",
    "Alkatrészek és felszerelések",
    "Hazai kereskedők",
    "Összehasonlítások",
    "Akciók",
  ],
  localServices: ["Vásárlás", "Kipróbálás", "Általános szerviz", "E-bike-szerviz"],
};
