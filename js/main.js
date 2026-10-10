(function () {
  const content = window.KEREKPARINDEX_CONTENT;
  const dialog = document.getElementById("dialog");
  const dialogTitle = document.getElementById("dialog-title");
  const dialogContent = document.getElementById("dialog-content");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const NA = (content && content.naLabel) || "Nincs ellenőrzött adatunk";
  let lastOpener = null;
  let searchMode = "termek";
  let cityComboOutside = null;

  const STATUS_LABEL = {
    ellenőrzött: "Ellenőrzött",
    előkészített: "Előkészítés alatt",
    hiányos: "Hiányos",
    archivált: "Archivált gyártói oldal",
    ellentmondás: "Ellentmondásos adat",
    hiányzó_adat: "Hiányzó adat",
  };

  const ROLE_LABEL = {
    eladas: "Eladás",
    szerviz: "Szerviz",
    "e-bike-szerviz": "E-bike szerviz",
  };

  const metricFallback = {
    wh: [
      "Az energia, amit magaddal viszel.",
      "A Wh (wattóra) a tárolható energiát jelzi. Több Wh nagyobb tartalékot jelenthet; a megtehető távot a terep és a rásegítés is befolyásolja.",
    ],
    nm: [
      "Rásegítés, amit emelkedőn is érzel.",
      "A Nm (newtonméter) a forgatónyomaték mértékegysége. A menetérzetet a vezérlés és az áttétel is alakítja; a nagyobb szám önmagában nem jelent jobb kerékpárt.",
    ],
    km: [
      "A távolság a körülményektől függ.",
      "A hatótáv becslés. Számít a terep, a terhelés, az időjárás és a rásegítés. A gyártói érték mellett nézd meg a megadott feltételeket is.",
    ],
  };
  const metricMap = { wh: "art-exp-wh", nm: "art-exp-nm", km: "art-exp-range" };

  function scrollBehavior() {
    return reduceMotion.matches ? "auto" : "smooth";
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function val(v) {
    if (v == null || v === "") return NA;
    return String(v);
  }

  function mdToHtml(md) {
    if (!md) return "";
    const lines = md.replace(/\r\n/g, "\n").split("\n");
    const out = [];
    let i = 0;
    let inUl = false;
    let inTable = false;

    function closeUl() {
      if (inUl) {
        out.push("</ul>");
        inUl = false;
      }
    }
    function closeTable() {
      if (inTable) {
        out.push("</tbody></table></div>");
        inTable = false;
      }
    }

    while (i < lines.length) {
      const line = lines[i];
      if (/^\|/.test(line) && lines[i + 1] && /^\|\s*-+/.test(lines[i + 1])) {
        closeUl();
        const headers = line.split("|").slice(1, -1).map(function (c) {
          return c.trim();
        });
        out.push("<div class='table-wrap'><table><thead><tr>");
        headers.forEach(function (h) {
          out.push("<th>" + esc(h) + "</th>");
        });
        out.push("</tr></thead><tbody>");
        i += 2;
        inTable = true;
        while (i < lines.length && /^\|/.test(lines[i])) {
          const cells = lines[i].split("|").slice(1, -1).map(function (c) {
            return c.trim();
          });
          out.push("<tr>");
          cells.forEach(function (c) {
            const display = c === "null" ? NA : c;
            const isUrl = /^https?:\/\//.test(display);
            out.push(
              "<td>" +
                (isUrl
                  ? '<a href="' +
                    esc(display) +
                    '" target="_blank" rel="noopener">' +
                    esc(display) +
                    "</a>"
                  : esc(display)) +
                "</td>"
            );
          });
          out.push("</tr>");
          i += 1;
        }
        closeTable();
        continue;
      }
      if (/^### /.test(line)) {
        closeUl();
        closeTable();
        out.push("<h4>" + inline(line.slice(4)) + "</h4>");
      } else if (/^## /.test(line)) {
        closeUl();
        closeTable();
        out.push("<h3>" + inline(line.slice(3)) + "</h3>");
      } else if (/^[-*] /.test(line)) {
        closeTable();
        if (!inUl) {
          out.push("<ul>");
          inUl = true;
        }
        out.push("<li>" + inline(line.slice(2)) + "</li>");
      } else if (!line.trim()) {
        closeUl();
        closeTable();
      } else {
        closeUl();
        closeTable();
        out.push("<p>" + inline(line) + "</p>");
      }
      i += 1;
    }
    closeUl();
    closeTable();
    return out.join("");
  }

  function inline(text) {
    let t = esc(text);
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    t = t.replace(
      /(https?:\/\/[^\s<]+)/g,
      '<a href="$1" target="_blank" rel="noopener">$1</a>'
    );
    return t;
  }

  function show(title, body, opener) {
    lastOpener = opener || document.activeElement;
    dialogTitle.textContent = title;
    dialogContent.innerHTML = body;
    if (!dialog.open) dialog.showModal();
  }

  function closeDialog() {
    dialog.close();
  }

  dialog.addEventListener("close", function () {
    if (lastOpener && typeof lastOpener.focus === "function") lastOpener.focus();
    lastOpener = null;
  });

  document.querySelector(".close-dialog").addEventListener("click", closeDialog);
  document.getElementById("dialog-ok").addEventListener("click", closeDialog);
  dialog.addEventListener("click", function (e) {
    if (e.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (
      e.clientX < r.left ||
      e.clientX > r.right ||
      e.clientY < r.top ||
      e.clientY > r.bottom
    ) {
      closeDialog();
    }
  });

  const PLANNED = {
    hasznalt: { title: "Adok-veszek" },
    tura: { title: "Túrák és útvonalak" },
    esemeny: { title: "Események" },
    akcio: { title: "Akciók" },
  };
  const PLANNED_BODY = "<p><strong>Hamarosan itt is böngészhetsz.</strong></p>";

  function brandById(id) {
    return content.brands.find(function (b) {
      return b.id === id;
    });
  }

  function brandByName(name) {
    const key = String(name || "").toLocaleLowerCase("hu");
    return content.brands.find(function (b) {
      return (
        b.name.toLocaleLowerCase("hu") === key ||
        b.slug === key ||
        b.id === "brand-" + key
      );
    });
  }

  function showPlanned(key, opener) {
    const info = PLANNED[key];
    if (!info) return;
    show(info.title, PLANNED_BODY, opener);
  }

  function labelStatus(status) {
    return STATUS_LABEL[status] || status;
  }

  function labelRole(role) {
    return ROLE_LABEL[role] || role;
  }
  function productById(id) {
    return content.products.find(function (p) {
      return p.id === id;
    });
  }
  function variantsForBrand(brandId) {
    return content.variants.filter(function (v) {
      const p = productById(v.productId);
      return p && p.brandId === brandId;
    });
  }
  function shopsForBrand(brandId) {
    return (content.shopsByBrand && content.shopsByBrand[brandId]) || [];
  }

  function statusBadge(status, flags) {
    const bits = [];
    if (status && status !== "ellenőrzött") bits.push(labelStatus(status));
    (flags || []).forEach(function (f) {
      bits.push(labelStatus(f));
    });
    if (!bits.length) return "";
    return (
      '<p class="meta-line"><span class="badge">' +
      esc(bits.join(" · ")) +
      "</span></p>"
    );
  }

  const CAT_LABEL = {
    mountain: "Mountain",
    road: "Országúti",
    gravel: "Gravel",
    trekking: "Trekking",
    kids: "Gyerek",
    "e-mountain": "E-MTB",
    "e-trekking": "E-trekking",
    "e-compact-folding": "Kompakt / összecsukható e-bike",
    "e-gravel": "E-gravel",
    "e-transport": "Szállító e-bike",
    "e-kids": "Gyerek e-bike",
    "e-bike": "E-bike",
    "e-mtb": "E-MTB",
    electric: "Elektromos",
    city: "Városi",
    fitness: "Fitness",
    "trekking-dual-sport": "Trekking / dual sport",
    cyclocross: "Cyclocross",
    triathlon: "Triatlon",
    bikes: "Kerékpárok",
    accessories: "Kiegészítők",
    "apparel-equipment": "Ruházat és felszerelés",
    "urban-mobility": "Városi mobilitás",
    bike: "Kerékpárok",
  };

  function renderBrand(brand, opener) {
    const vars = variantsForBrand(brand.id);
    const shops = shopsForBrand(brand.id);
    let html = statusBadge(brand.status, brand.dataFlags);
    html += "<p>" + esc(brand.shortDescription || "") + "</p>";
    if (brand.productCategories && brand.productCategories.length) {
      html +=
        "<p class='meta-line'>Termékcsoportok: " +
        esc(
          brand.productCategories
            .map(function (c) {
              return CAT_LABEL[c] || c;
            })
            .join(", ")
        ) +
        "</p>";
    }
    if (brand.officialWebsite) {
      html +=
        '<p><a href="' +
        esc(brand.officialWebsite) +
        '" target="_blank" rel="noopener">Hivatalos oldal ↗</a>';
      if (brand.hungaryRelatedWebsite) {
        html +=
          ' · <a href="' +
          esc(brand.hungaryRelatedWebsite) +
          '" target="_blank" rel="noopener">Magyar vonatkozású oldal ↗</a>';
      }
      html += "</p>";
    }
    html += "<h3>Modellváltozatok</h3>";
    if (!vars.length) {
      html +=
        "<p>Ehhez a márkához még nincs közzétett modellváltozat.</p>";
    } else {
      html += '<div class="dialog-grid">';
      vars.forEach(function (v) {
        html +=
          '<button type="button" class="linkish" data-open-variant="' +
          esc(v.id) +
          '">' +
          esc(v.exactName) +
          "</button>";
      });
      html += "</div>";
    }
    html += "<h3>Márkát forgalmazó üzletek</h3>";
    html +=
      "<p class='note'>Ha egy üzlet forgalmazza a márkát, az nem jelenti automatikusan, hogy az adott modell raktáron van, vagy kipróbálható.</p>";
    if (!shops.length) {
      html +=
        "<p>Ehhez a márkához még nincs forrással igazolt üzletkapcsolatunk.</p>";
    } else {
      html += "<ul>";
      shops.forEach(function (s) {
        html +=
          "<li><button type='button' class='linkish' data-open-location='" +
          esc(s.locationId) +
          "'>" +
          esc(s.name) +
          (s.city ? " · " + esc(s.city) : "") +
          "</button></li>";
      });
      html += "</ul>";
    }
    show(brand.name, html, opener);
    bindDialogNav();
  }

  function renderVariant(variant, opener) {
    const product = productById(variant.productId);
    const brand = product ? brandById(product.brandId) : null;
    const weight =
      variant.weightDisplay ||
      (variant.weightKg != null
        ? String(variant.weightKg).replace(".", ",") +
          (variant.weighingConditions
            ? " (" + variant.weighingConditions + ")"
            : " (mérési feltétel nélkül)")
        : "Ehhez a változathoz nincs ellenőrzött tömegadatunk.");
    let html = statusBadge(variant.status, variant.dataFlags);
    if (brand) {
      html +=
        "<p><button type='button' class='linkish' data-open-brand='" +
        esc(brand.id) +
        "'>" +
        esc(brand.name) +
        "</button></p>";
    }
    if ((variant.dataFlags || []).indexOf("archivált") !== -1) {
      html +=
        "<p class='note'>Archivált gyártói oldal: a specifikáció olvasható. Azt, hogy a modellt jelenleg is gyártják, nem igazoltuk — ez önmagában nem jelenti, hogy ne lehetne megvásárolni.</p>";
    }
    html += "<ul class='spec-list'>";
    html += "<li><strong>Típus:</strong> " + esc(val(variant.bikeType)) + "</li>";
    html +=
      "<li><strong>Motor:</strong> " + esc(val(variant.motorExactType)) + "</li>";
    html +=
      "<li><strong>Nyomaték:</strong> " +
      esc(val(variant.torqueNm)) +
      (variant.torqueNm != null ? " Nm" : "") +
      "</li>";
    html +=
      "<li><strong>Akkumulátor:</strong> " +
      esc(val(variant.batteryWh)) +
      (variant.batteryWh != null ? " Wh" : "") +
      (variant.batteryExact ? " · " + esc(variant.batteryExact) : "") +
      "</li>";
    html +=
      "<li><strong>Hajtás:</strong> " +
      esc(val(variant.drivetrain)) +
      (variant.drivetrainNote
        ? " <em>(" + esc(variant.drivetrainNote) + ")</em>"
        : "") +
      "</li>";
    html +=
      "<li><strong>Fék:</strong> " +
      esc(val(variant.brakesDisplay || variant.brakes)) +
      "</li>";
    html += "<li><strong>Tömeg:</strong> " + esc(weight) + "</li>";
    html += "</ul>";
    const unresolved = variant.unresolvedFields || [];
    if (unresolved.indexOf("tires") !== -1) {
      html +=
        "<p class='note'>A gumi megnevezése a gyártói oldalon belül eltérő, ezért gumitípust nem közlünk ellenőrzött adatként.</p>";
    }
    if (variant.sourceUrl) {
      html +=
        '<p><a href="' +
        esc(variant.sourceUrl) +
        '" target="_blank" rel="noopener">Gyártói forrás ↗</a></p>';
    }
    if (brand) {
      const shops = shopsForBrand(brand.id);
      html += "<h3>Márkát forgalmazó üzletek</h3>";
      html +=
        "<p class='note'>Az alábbi üzletek a márkát forgalmazzák. Konkrét modellkészletről vagy kipróbálásról itt nincs adatunk.</p>";
      if (!shops.length) html += "<p>" + esc(NA) + "</p>";
      else {
        html += "<ul>";
        shops.forEach(function (s) {
          html +=
            "<li><button type='button' class='linkish' data-open-location='" +
            esc(s.locationId) +
            "'>" +
            esc(s.name) +
            (s.city ? " · " + esc(s.city) : "") +
            "</button></li>";
        });
        html += "</ul>";
      }
    }
    show(variant.exactName, html, opener);
    bindDialogNav();
  }

  function renderLocation(loc, opener) {
    const services =
      (content.servicesByLocation && content.servicesByLocation[loc.id]) || [];
    const addr = loc.address || {};
    let html = statusBadge(loc.status);
    html += "<p>" + esc(addr.raw || "") + "</p>";
    if (loc.website) {
      html +=
        '<p><a href="' +
        esc(loc.website) +
        '" target="_blank" rel="noopener">Weboldal ↗</a></p>';
    }
    if (loc.phone && loc.phone.length) {
      html += "<p>Telefon: " + esc(loc.phone.join(" · ")) + "</p>";
    }
    if (loc.email && loc.email.length) {
      html +=
        "<p>E-mail: " +
        esc(
          (Array.isArray(loc.email) ? loc.email : [loc.email]).join(" · ")
        ) +
        "</p>";
    }
    if (loc.openingHours) {
      const hours =
        typeof loc.openingHours === "string"
          ? loc.openingHours
          : loc.openingHours.summary || "";
      if (hours) html += "<p>Nyitvatartás: " + esc(hours) + "</p>";
    }
    html += "<h3>Szolgáltatások</h3><ul>";
    if (!services.length) html += "<li>" + esc(NA) + "</li>";
    else {
      services.forEach(function (s) {
        html +=
          "<li>" +
          esc(labelRole(s.role)) +
          (s.sourceUrl
            ? ' · <a href="' +
              esc(s.sourceUrl) +
              '" target="_blank" rel="noopener">Forrás ↗</a>'
            : "") +
          "</li>";
      });
    }
    html += "</ul><h3>Forgalmazott márkák</h3>";
    html +=
      "<p class='note'>Itt csak annyi igazolt: az üzlet a márkát forgalmazza. Konkrét modellkészletről vagy kipróbálásról nincs adatunk.</p>";
    const links = (loc.brandLinks || []).filter(function (b) {
      return b.inCatalog;
    });
    if (!links.length) {
      html += "<p>Ehhez a telephelyhez még nincs forrással igazolt katalógusmárka.</p>";
    } else {
      html += "<ul>";
      links.forEach(function (b) {
        html +=
          "<li><button type='button' class='linkish' data-open-brand='" +
          esc(b.brandId) +
          "'>" +
          esc(b.brandName) +
          "</button></li>";
      });
      html += "</ul>";
    }
    show(loc.name, html, opener);
    bindDialogNav();
  }

  function renderPlaces(filter, opener) {
    const q = filter || {};
    let locs = content.locations.slice();
    if (q.city) {
      locs = locs.filter(function (l) {
        return (l.address || {}).city === q.city;
      });
    }
    if (q.brandId) {
      locs = locs.filter(function (l) {
        return (l.brandLinks || []).some(function (b) {
          return b.brandId === q.brandId;
        });
      });
    }
    if (q.role) {
      locs = locs.filter(function (l) {
        const svcs = content.servicesByLocation[l.id] || [];
        return svcs.some(function (s) {
          return (
            s.role === q.role ||
            (q.role === "szerviz" && s.role.indexOf("szerviz") !== -1)
          );
        });
      });
    }
    const cities = Array.from(
      new Set(
        content.locations.map(function (l) {
          return (l.address || {}).city;
        })
      )
    )
      .filter(Boolean)
      .sort(function (a, b) {
        return a.localeCompare(b, "hu");
      });

    const cityLabel = q.city || "Minden település";
    let html =
      "<p>Szűrj település, márka vagy szolgáltatás szerint. A listában ellenőrzött telephelyek szerepelnek.</p>";
    html += '<form class="place-filter" id="place-filter">';
    html +=
      '<div class="city-combo" data-city-combo>' +
      '<span class="city-combo-caption" id="city-combo-label">Település</span>' +
      '<input type="hidden" name="city" id="place-city-value" value="' +
      esc(q.city || "") +
      '">' +
      '<button type="button" class="city-combo-trigger" id="city-combo-trigger" role="combobox" aria-expanded="false" aria-haspopup="listbox" aria-controls="city-listbox" aria-labelledby="city-combo-label" aria-autocomplete="list">' +
      esc(cityLabel) +
      "</button>" +
      '<div class="city-combo-panel" id="city-combo-panel" hidden>' +
      '<input type="search" class="city-combo-search" id="city-combo-search" placeholder="Település keresése…" autocomplete="off" aria-label="Település keresése" aria-controls="city-listbox">' +
      '<ul class="city-combo-list" role="listbox" id="city-listbox" aria-labelledby="city-combo-label"></ul>' +
      '<p class="city-combo-empty" id="city-combo-empty" hidden>Nincs ilyen település a listában.</p>' +
      "</div></div>";
    html += '<label>Márka <select name="brand"><option value="">Mind</option>';
    content.brands.forEach(function (b) {
      html +=
        '<option value="' +
        esc(b.id) +
        '"' +
        (q.brandId === b.id ? " selected" : "") +
        ">" +
        esc(b.name) +
        "</option>";
    });
    html += "</select></label>";
    html +=
      '<label>Szolgáltatás <select name="role"><option value="">Mind</option>';
    ["eladas", "szerviz", "e-bike-szerviz"].forEach(function (r) {
      html +=
        '<option value="' +
        esc(r) +
        '"' +
        (q.role === r ? " selected" : "") +
        ">" +
        esc(labelRole(r)) +
        "</option>";
    });
    html +=
      '</select></label><button type="submit" class="go">Szűrés ↗</button></form>';
    html +=
      "<p class='meta-line'>" + locs.length + " telephely</p><ul class='place-list'>";
    locs.forEach(function (l) {
      const roles = (content.servicesByLocation[l.id] || [])
        .map(function (s) {
          return labelRole(s.role);
        })
        .join(", ");
      html +=
        "<li><button type='button' class='linkish' data-open-location='" +
        esc(l.id) +
        "'>" +
        esc(l.name) +
        "</button> · " +
        esc((l.address || {}).city || "") +
        (roles ? " · " + esc(roles) : "") +
        "</li>";
    });
    html += "</ul>";
    show("Üzletek és szervizek", html, opener);
    const form = document.getElementById("place-filter");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const fd = new FormData(form);
        renderPlaces(
          {
            city: fd.get("city") || "",
            brandId: fd.get("brand") || "",
            role: fd.get("role") || "",
          },
          opener
        );
      });
      initCityCombo(form, cities, q.city || "", opener);
    }
    bindDialogNav();
  }

  function initCityCombo(form, cities, selectedCity, opener) {
    const root = form.querySelector("[data-city-combo]");
    if (!root) return;
    const trigger = root.querySelector("#city-combo-trigger");
    const panel = root.querySelector("#city-combo-panel");
    const search = root.querySelector("#city-combo-search");
    const list = root.querySelector("#city-listbox");
    const empty = root.querySelector("#city-combo-empty");
    const hidden = root.querySelector("#place-city-value");
    const ALL = "Minden település";
    let open = false;
    let activeIndex = 0;
    let options = [];

    function currentFilters(cityOverride) {
      const fd = new FormData(form);
      return {
        city: cityOverride !== undefined ? cityOverride : fd.get("city") || "",
        brandId: fd.get("brand") || "",
        role: fd.get("role") || "",
      };
    }

    function rankCities(query) {
      const q = norm(query);
      if (!q) {
        return cities.slice();
      }
      const exact = [];
      const starts = [];
      const contains = [];
      cities.forEach(function (c) {
        const n = norm(c);
        if (n === q) exact.push(c);
        else if (n.indexOf(q) === 0) starts.push(c);
        else if (n.indexOf(q) !== -1) contains.push(c);
      });
      return exact.concat(starts, contains);
    }

    function renderOptions(query) {
      const ranked = rankCities(query);
      options = [{ value: "", label: ALL }].concat(
        ranked.map(function (c) {
          return { value: c, label: c };
        })
      );
      const q = norm(query);
      empty.hidden = !(q && ranked.length === 0);
      list.innerHTML = "";
      options.forEach(function (opt, i) {
        const li = document.createElement("li");
        li.setAttribute("role", "option");
        li.id = "city-opt-" + i;
        li.dataset.value = opt.value;
        li.textContent = opt.label;
        if (opt.value === (hidden.value || "") || (!opt.value && !hidden.value)) {
          li.setAttribute("aria-selected", "true");
        } else {
          li.setAttribute("aria-selected", "false");
        }
        li.addEventListener("mousedown", function (e) {
          e.preventDefault();
          choose(opt.value);
        });
        list.appendChild(li);
      });
      activeIndex = 0;
      paintActive();
    }

    function paintActive() {
      const items = list.querySelectorAll('[role="option"]');
      items.forEach(function (el, i) {
        const on = i === activeIndex;
        el.classList.toggle("is-active", on);
        if (on) {
          trigger.setAttribute("aria-activedescendant", el.id);
          el.scrollIntoView({ block: "nearest" });
        }
      });
    }

    function setOpen(next) {
      open = next;
      panel.hidden = !open;
      trigger.setAttribute("aria-expanded", String(open));
      if (open) {
        search.value = "";
        renderOptions("");
        window.setTimeout(function () {
          search.focus();
        }, 0);
      } else {
        trigger.setAttribute("aria-activedescendant", "");
      }
    }

    function choose(value) {
      hidden.value = value || "";
      trigger.textContent = value || ALL;
      setOpen(false);
      renderPlaces(currentFilters(value || ""), opener);
    }

    trigger.addEventListener("click", function () {
      setOpen(!open);
    });
    trigger.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        if (!open) setOpen(true);
        else if (e.key === "Enter") choose(options[activeIndex] && options[activeIndex].value);
      } else if (e.key === "Escape" && open) {
        e.preventDefault();
        setOpen(false);
        trigger.focus();
      }
    });

    search.addEventListener("input", function () {
      renderOptions(search.value);
    });
    search.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (!options.length) return;
        activeIndex = Math.min(options.length - 1, activeIndex + 1);
        paintActive();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (!options.length) return;
        activeIndex = Math.max(0, activeIndex - 1);
        paintActive();
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (options[activeIndex]) choose(options[activeIndex].value);
      } else if (e.key === "Escape") {
        e.preventDefault();
        setOpen(false);
        trigger.focus();
      }
    });

    if (cityComboOutside) {
      document.removeEventListener("pointerdown", cityComboOutside, true);
      cityComboOutside = null;
    }
    cityComboOutside = function (ev) {
      if (!open) return;
      if (!root.contains(ev.target)) setOpen(false);
    };
    document.addEventListener("pointerdown", cityComboOutside, true);
    dialog.addEventListener(
      "close",
      function () {
        if (cityComboOutside) {
          document.removeEventListener("pointerdown", cityComboOutside, true);
          cityComboOutside = null;
        }
      },
      { once: true }
    );
  }

  function renderArticle(article, opener) {
    show(article.title, statusBadge(article.status) + mdToHtml(article.bodyMarkdown), opener);
  }

  function renderExplainers(opener) {
    let html =
      "<p>Rövid magyarázók: motor, nyomaték (Nm), akkukapacitás (Wh), hatótáv, tömeg és szervizháttér.</p><ul>";
    content.explainers.forEach(function (a) {
      html +=
        "<li><button type='button' class='linkish' data-open-explainer='" +
        esc(a.id) +
        "'>" +
        esc(a.title) +
        "</button></li>";
    });
    html += "</ul><h3>Összehasonlítások</h3><ul>";
    content.comparisons.forEach(function (a) {
      html +=
        "<li><button type='button' class='linkish' data-open-comparison='" +
        esc(a.id) +
        "'>" +
        esc(a.title) +
        "</button></li>";
    });
    html += "</ul>";
    show("Magyarázók és összehasonlítások", html, opener);
    bindDialogNav();
  }

  function renderComparisons(opener) {
    let html =
      "<p>Három összehasonlítás gyártói adatokból. Nincs saját menetpróba, és nincs abszolút győztes.</p><ul>";
    content.comparisons.forEach(function (a) {
      html +=
        "<li><button type='button' class='linkish' data-open-comparison='" +
        esc(a.id) +
        "'>" +
        esc(a.title) +
        "</button></li>";
    });
    html += "</ul>";
    show("E-bike összehasonlítások", html, opener);
    bindDialogNav();
  }

  function renderAllBrands(opener) {
    let html = "<p>" + esc(content.notice) + '</p><div class="dialog-grid">';
    content.brands.forEach(function (b) {
      html +=
        '<button type="button" class="linkish" data-open-brand="' +
        esc(b.id) +
        '">' +
        esc(b.name) +
        (b.status !== "ellenőrzött" ? " · " + esc(labelStatus(b.status)) : "") +
        "</button>";
    });
    html += "</div>";
    show("Márkák", html, opener);
    bindDialogNav();
  }

  function bindDialogNav() {
    dialogContent.querySelectorAll("[data-open-brand]").forEach(function (el) {
      el.addEventListener("click", function () {
        const b = brandById(el.getAttribute("data-open-brand"));
        if (b) renderBrand(b, el);
      });
    });
    dialogContent.querySelectorAll("[data-open-variant]").forEach(function (el) {
      el.addEventListener("click", function () {
        const v = content.variants.find(function (x) {
          return x.id === el.getAttribute("data-open-variant");
        });
        if (v) renderVariant(v, el);
      });
    });
    dialogContent.querySelectorAll("[data-open-location]").forEach(function (el) {
      el.addEventListener("click", function () {
        const loc = content.locations.find(function (x) {
          return x.id === el.getAttribute("data-open-location");
        });
        if (loc) renderLocation(loc, el);
      });
    });
    dialogContent.querySelectorAll("[data-open-explainer]").forEach(function (el) {
      el.addEventListener("click", function () {
        const a = content.explainers.find(function (x) {
          return x.id === el.getAttribute("data-open-explainer");
        });
        if (a) renderArticle(a, el);
      });
    });
    dialogContent.querySelectorAll("[data-open-comparison]").forEach(function (el) {
      el.addEventListener("click", function () {
        const a = content.comparisons.find(function (x) {
          return x.id === el.getAttribute("data-open-comparison");
        });
        if (a) renderArticle(a, el);
      });
    });
  }

  function paintStories() {
    const host = document.getElementById("stories");
    if (!host || !content) return;
    const wh = content.explainers.find(function (a) {
      return a.id === "art-exp-wh";
    });
    const comfort = content.comparisons.find(function (a) {
      return a.id === "art-cmp-city-comfort";
    });
    const emtb = content.comparisons.find(function (a) {
      return a.id === "art-cmp-e-mtb";
    });
    const cards = [
      {
        featured: true,
        tag: "ÖSSZEHASONLÍTÁS",
        title: comfort ? comfort.title : "Városi e-bike összehasonlítás",
        body: "Gyártói adatok és mérési feltételek — abszolút győztes nélkül.",
        article: comfort,
        artClass: "",
      },
      {
        featured: false,
        tag: "MAGYARÁZÓ",
        title: wh ? wh.title : "Akkukapacitás (Wh)",
        body: "Mit árul el a Wh, és mit nem?",
        article: wh,
        artClass: "coral",
      },
      {
        featured: false,
        tag: "E-MTB",
        title: emtb ? emtb.title : "E-MTB összehasonlítás",
        body: "Merevvázas és összteleszkópos felépítés, világosan elválasztva.",
        article: emtb,
        artClass: "lav",
      },
    ];
    host.innerHTML = "";
    cards.forEach(function (c) {
      const btn = document.createElement("button");
      btn.className = "story" + (c.featured ? " featured" : "");
      btn.type = "button";
      btn.innerHTML =
        '<div class="art ' +
        esc(c.artClass) +
        '"><svg viewBox="0 0 500 220" aria-hidden="true"><use href="#bike" x="95" y="40" width="330" height="175" style="color:#ffab80"/></svg><span class="tag">' +
        esc(c.tag) +
        '</span></div><div class="story-body"><h3>' +
        esc(c.title) +
        "</h3><p>" +
        esc(c.body) +
        '</p><div class="meta"><span>Gyártói adatok</span><span>↗</span></div></div>';
      btn.addEventListener("click", function () {
        if (c.article) renderArticle(c.article, btn);
      });
      host.appendChild(btn);
    });
  }

  function activateMetric(btn) {
    document.querySelectorAll("[data-metric]").forEach(function (tab) {
      const on = tab === btn;
      tab.setAttribute("aria-pressed", String(on));
      tab.setAttribute("aria-selected", String(on));
    });
    const key = btn.dataset.metric;
    let title = metricFallback[key][0];
    let body = metricFallback[key][1];
    if (content) {
      const art = content.explainers.find(function (a) {
        return a.id === metricMap[key];
      });
      if (art) {
        title = art.title;
        const paras = art.bodyMarkdown
          .split("\n")
          .filter(function (l) {
            return (
              l &&
              !l.startsWith("#") &&
              !l.startsWith("-") &&
              !l.startsWith("|") &&
              !l.startsWith("*")
            );
          })
          .slice(0, 2);
        body = paras.join(" ");
      }
    }
    const box = document.getElementById("metric-copy");
    box.innerHTML =
      "<strong>" + esc(title) + "</strong><br>" + esc(body);
  }

  function norm(s) {
    return String(s == null ? "" : s)
      .toLocaleLowerCase("hu")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function locationRoleLine(loc) {
    const city = ((loc.address || {}).city || "").trim();
    const seen = {};
    const roles = ((content.servicesByLocation && content.servicesByLocation[loc.id]) || [])
      .map(function (s) {
        return labelRole(s.role);
      })
      .filter(function (r) {
        if (!r || seen[r]) return false;
        seen[r] = true;
        return true;
      });
    return [city, roles.join(", ")].filter(Boolean).join(" · ");
  }

  /** Location hits from published content: name, city, address; exact city first. */
  function matchLocationHits(q) {
    const exactCity = [];
    const cityPartial = [];
    const other = [];
    (content.locations || []).forEach(function (l) {
      const city = (l.address || {}).city || "";
      const raw = (l.address || {}).raw || "";
      const nCity = norm(city);
      const nName = norm(l.name);
      const nRaw = norm(raw);
      if (q) {
        const cityExact = nCity === q;
        const cityInc = !cityExact && nCity.indexOf(q) !== -1;
        const nameOrAddr =
          nName.indexOf(q) !== -1 || nRaw.indexOf(q) !== -1;
        if (!cityExact && !cityInc && !nameOrAddr) return;
        const hit = {
          type: "Üzlet",
          label: l.name,
          sub: locationRoleLine(l),
          open: function () {
            renderLocation(l);
          },
        };
        if (cityExact) exactCity.push(hit);
        else if (cityInc) cityPartial.push(hit);
        else other.push(hit);
      } else {
        other.push({
          type: "Üzlet",
          label: l.name,
          sub: locationRoleLine(l),
          open: function () {
            renderLocation(l);
          },
        });
      }
    });
    return exactCity.concat(cityPartial, other);
  }

  function showResultsPanel(title, items, status) {
    const panel = document.getElementById("results");
    const grid = document.getElementById("results-grid");
    document.getElementById("results-title").textContent = title;
    document.getElementById("result-status").textContent = status;
    grid.innerHTML = "";
    items.forEach(function (item) {
      const b = document.createElement("button");
      b.className = "result";
      b.type = "button";
      b.innerHTML =
        "<small>" +
        esc(item.type) +
        " ↗</small><h3>" +
        esc(item.label) +
        "</h3><p>" +
        esc(item.sub || "") +
        "</p>";
      b.addEventListener("click", item.open);
      grid.appendChild(b);
    });
    panel.hidden = false;
    panel.scrollIntoView({ behavior: scrollBehavior(), block: "start" });
  }

  function runSearch(qRaw) {
    if (!content) return;
    const msg = document.getElementById("search-message");

    if (searchMode === "hasznalt" || searchMode === "tura" || searchMode === "esemeny") {
      document.getElementById("results").hidden = true;
      msg.hidden = false;
      msg.textContent = "Hamarosan itt is böngészhetsz.";
      showPlanned(searchMode === "hasznalt" ? "hasznalt" : searchMode);
      return;
    }

    const q = norm(qRaw);
    const hits = [];
    const locationHits = q || searchMode === "hely" ? matchLocationHits(q) : [];

    if (searchMode === "termek" || !searchMode) {
      content.brands.forEach(function (b) {
        if (!q || norm(b.name).includes(q) || norm(b.shortDescription || "").includes(q)) {
          hits.push({
            type: "Márka",
            label: b.name,
            sub: b.status !== "ellenőrzött" ? labelStatus(b.status) : "",
            open: function () {
              renderBrand(b);
            },
          });
        }
      });
      content.variants.forEach(function (v) {
        if (
          !q ||
          norm(v.exactName).includes(q) ||
          norm(v.motorExactType || "").includes(q)
        ) {
          const product = productById(v.productId);
          const brand = product ? brandById(product.brandId) : null;
          hits.push({
            type: "Modell",
            label: v.exactName,
            sub: [brand && brand.name, v.bikeType].filter(Boolean).join(" · "),
            open: function () {
              renderVariant(v);
            },
          });
        }
      });
      if (q) {
        (content.explainers || []).forEach(function (a) {
          if (
            norm(a.title).includes(q) ||
            norm(a.bodyMarkdown || "").includes(q)
          ) {
            hits.push({
              type: "Magyarázó",
              label: a.title,
              sub: "Rövid magyarázat",
              open: function () {
                renderArticle(a);
              },
            });
          }
        });
        (content.comparisons || []).forEach(function (a) {
          if (
            norm(a.title).includes(q) ||
            norm(a.bodyMarkdown || "").includes(q)
          ) {
            hits.push({
              type: "Összehasonlítás",
              label: a.title,
              sub: "Gyártói adatok",
              open: function () {
                renderArticle(a);
              },
            });
          }
        });
        // Default hero: keep city/shop intent — append published place hits.
        locationHits.forEach(function (h) {
          hits.push(h);
        });
      }
    }
    if (searchMode === "hely") {
      locationHits.forEach(function (h) {
        hits.push(h);
      });
    }

    if (!q && searchMode === "termek") {
      msg.hidden = true;
      showResultsPanel(
        "Kerékpárok és felszerelések",
        hits.slice(0, 12),
        hits.length + " találat"
      );
      return;
    }
    msg.hidden = false;
    if (!hits.length) {
      // Category empty but places match → surface place hits (no false "nincs találat").
      if (q && locationHits.length && searchMode !== "hely") {
        msg.textContent =
          locationHits.length +
          " helytalálat (a „Helyek” kategóriában is kereshetsz)";
        showResultsPanel(
          "Helytalálatok",
          locationHits.slice(0, 24),
          locationHits.length + " találat"
        );
        return;
      }
      msg.textContent =
        "Nincs egyezés. Próbáld például: CUBE, Trek, Debrecen, akkukapacitás.";
      document.getElementById("results").hidden = true;
      return;
    }
    msg.textContent = hits.length + " találat";
    showResultsPanel(
      "Keresési találatok",
      hits.slice(0, 24),
      hits.length + " találat"
    );
  }

  if (!content) {
    document.getElementById("search-message").hidden = false;
    document.getElementById("search-message").textContent =
      "A tartalmi csomag nem töltődött be.";
    return;
  }

  paintStories();

  document.querySelectorAll("[data-brand]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const b = brandByName(btn.dataset.brand);
      if (b) renderBrand(b, btn);
      else show(btn.dataset.brand, "<p>" + esc(NA) + "</p>", btn);
    });
  });

  document.getElementById("all-brands").addEventListener("click", function () {
    renderAllBrands(this);
  });

  document.querySelectorAll("[data-search]").forEach(function (b) {
    b.addEventListener("click", function () {
      searchMode = b.dataset.search;
      document.querySelectorAll("[data-search]").forEach(function (x) {
        x.setAttribute("aria-pressed", String(x === b));
      });
      document.getElementById("query").placeholder = {
        termek: "Márka, kerékpár, alkatrész…",
        hasznalt: "Mit vennél vagy cserélnél?",
        hely: "Település, üzlet, szerviz, kölcsönző…",
        tura: "Ország, térség, útvonal…",
        esemeny: "Esemény, helyszín…",
      }[searchMode];
    });
  });

  document.getElementById("search").addEventListener("submit", function (e) {
    e.preventDefault();
    runSearch(document.getElementById("query").value);
  });

  document.getElementById("hide-results").addEventListener("click", function () {
    document.getElementById("results").hidden = true;
    document.getElementById("query").focus();
  });

  document.querySelectorAll("[data-open]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      const key = el.getAttribute("data-open");
      if (!key) return;
      if (el.tagName === "A") e.preventDefault();
      if (key === "brands") renderAllBrands(el);
      else if (key === "places") renderPlaces({}, el);
      else if (key === "explainers") renderExplainers(el);
      else if (key === "comparisons") renderComparisons(el);
    });
  });

  document.querySelectorAll("[data-planned]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      const key = el.getAttribute("data-planned");
      if (!key || !PLANNED[key]) return;
      if (el.tagName === "A") e.preventDefault();
      // Allow in-page scroll for section anchors, then show status
      if (el.getAttribute("href") && el.getAttribute("href").charAt(0) === "#") {
        const target = document.querySelector(el.getAttribute("href"));
        if (target) {
          target.scrollIntoView({ behavior: scrollBehavior(), block: "start" });
        }
      }
      showPlanned(key, el);
    });
  });

  const countrySelect = document.getElementById("country");
  if (countrySelect) {
    countrySelect.addEventListener("change", function () {
      const value = countrySelect.value;
      document.querySelectorAll("[data-country]").forEach(function (el) {
        el.hidden = value !== "all" && el.dataset.country !== value;
      });
    });
  }

  document.querySelectorAll("[data-metric]").forEach(function (btn, index, all) {
    btn.addEventListener("click", function () {
      activateMetric(btn);
    });
    btn.addEventListener("keydown", function (e) {
      const tabs = Array.prototype.slice.call(all);
      let next = null;
      if (e.key === "ArrowRight" || e.key === "ArrowDown")
        next = tabs[(index + 1) % tabs.length];
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp")
        next = tabs[(index - 1 + tabs.length) % tabs.length];
      if (!next) return;
      e.preventDefault();
      activateMetric(next);
      next.focus();
    });
  });

  const menu = document.querySelector(".menu-btn");
  const nav = document.getElementById("nav");
  function closeMenu() {
    nav.classList.remove("open");
    menu.setAttribute("aria-expanded", "false");
    menu.setAttribute("aria-label", "Menü megnyitása");
  }
  menu.addEventListener("click", function () {
    const open = nav.classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute("aria-label", open ? "Menü bezárása" : "Menü megnyitása");
  });
  nav.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", closeMenu);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("open")) {
      closeMenu();
      menu.focus();
    }
  });
})();
