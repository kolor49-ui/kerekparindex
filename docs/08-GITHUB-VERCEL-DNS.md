# GitHub, Vercel és DNS — kerekparindex.hu

## Cél

Statikus C · ORBIT főoldal publikálása Vercelen, domain: `kerekparindex.hu` (+ `www`).

## GitHub

- Távoli repo: a `kolor49-ui` fiók alatt (helyi `gh` bejelentkezés szerint).
- Branch: `main`
- Tartalom: `index.html`, `css/`, `js/`, `data/`, `reference/`, `docs/` (prototípus + specifikáció)

## Vercel

- Framework preset: **Other** (tiszta statikus HTML)
- Root Directory: `.` (projekt gyökér)
- Build Command: *(üres / nincs)*
- Output Directory: `.` (vagy hagyományosan a gyökér, ahol az `index.html` van)
- Install Command: *(üres)*

A `vercel.json` a repo gyökerében van (clean URLs + alap biztonsági headerek).

## DNS — mit állíts át (Fontana / jelenlegi panel)

A jelenlegi A rekordok a **185.208.224.100** IP-re mutatnak (régi webtárhely). A weboldalhoz Vercelre kell mutatniuk. **Az e-mail rekordokat ne töröld**, ha a levelezés ugyanott marad.

### Webhez szükséges (Vercel)

| Típus | Név (host) | Érték | TTL | Megjegyzés |
| --- | --- | --- | --- | --- |
| **A** | `kerekparindex.hu.` vagy `@` | **`76.76.21.21`** | 1 óra | Apex / gyökér domain → Vercel |
| **CNAME** | `www` | **`cname.vercel-dns.com.`** | 1 óra | www aldomain → Vercel |

> A Vercel projekt Domains kártyáján megjelenő A / CNAME érték a mérvadó. Ha a dashboard más IP-t vagy projekt-specifikus CNAME-et ír (pl. `….vercel-dns-017.com`), **azt** használd.

### Jelenlegi rekordok — mi legyen velük

| Jelenlegi | Javaslat |
| --- | --- |
| A `kerekparindex.hu.` → `185.208.224.100` | **Cseréld** → `76.76.21.21` (vagy a Vercel által mutatott A) |
| A `www.kerekparindex.hu.` → `185.208.224.100` | **Töröld az A-t**, helyette **CNAME** `www` → `cname.vercel-dns.com.` |
| A `*.kerekparindex.hu.` → `185.208.224.100` | Opcionális. Ha nem kell wildcard a régi szerverre, töröld vagy hagyd; a www-t a CNAME kezeli |
| A `mail.kerekparindex.hu.` → `185.208.224.100` | **Maradjon**, ha a levelezés ott van |
| MX `kerekparindex.hu.` → `mail.kerekparindex.hu` | **Maradjon** |
| SPF / DMARC TXT | **Maradjon** (e-mail) |

### CAA (ajánlott, ha még nincs)

Ha a szolgáltató kéri, vagy SSL problémád van:

| Típus | Név | Érték |
| --- | --- | --- |
| CAA | `@` | `0 issue "letsencrypt.org"` |

(Vercel Let’s Encrypttel állít ki tanúsítványt.)

## Lépésről lépésre

1. GitHub repo létrehozása + `main` push.
2. Vercel: Import Git Repository → válaszd a repót → Deploy.
3. Vercel → Project → **Settings → Domains** → add hozzá: `kerekparindex.hu` és `www.kerekparindex.hu`.
4. A Domains kártyán látható A / CNAME értékeket írd be a DNS panelbe (fenti táblázat szerint).
5. Mentés után várd meg a propagációt (perc–óra). Vercel zöld pipát mutat, ha a tanúsítvány kész.
6. Ellenőrzés terminálból:
   ```bash
   dig +short A kerekparindex.hu
   dig +short CNAME www.kerekparindex.hu
   ```

## Fontos

- A **185.208.224.100** a jelenlegi (régi) tárhely IP-je — **nem** Vercel.
- Vercel tipikus apex A: **`76.76.21.21`**.
- Ne töröld az MX / mail / SPF rekordokat, különben elromlik a levelezés.
- Amíg a DNS nem terjed, a régi oldal / hibás SSL látszódhat.
