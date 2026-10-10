# Design-döntés — ORBIT Compact

Dátum: 2026-10-10  
Státusz: **elfogadott főoldali elrendezési referencia**

## Döntés

Az ORBIT Compact változat (`reference/kerekparindex-orbit-compact.html`) a hivatalos főoldali elrendezés mobilon és asztalon. Felváltja a korábbi nagy herós C · ORBIT főoldalt (`reference/kerekparindex-v2-c.html`), amely történelmi referenciaként megmarad.

## Megőrzött

- ORBIT színek, tipográfia (Arial), illusztráció, levendula e-bike blokk
- Prototípus-interakciók: kereső, dialógusok, Wh/Nm/km magyarázó
- Korábbi a11y javítások: tab szerepek (`tablist` / `tab` / `tabpanel`), Escape + fókusz-vissza dialógusnál, `prefers-reduced-motion`

## Compact jellegzetességek

- Kompakt hero (kisebb H1, rövid leírás, asztalon kisebb illusztráció; mobilon illusztráció rejtve)
- Sorrend: hero → márkák → kereső → kategóriák → aktualis → elektromos → helyek
- Mobil: hamburger menü (`menu-toggle` + `aria-expanded`)
- Kategóriák ikon+szöveg rács; tartalmi kártyák rövid bekezdéssel

## Nem része ennek a körnek

Éles Vercel publikálás — csak helyi integráció és review csomag.
