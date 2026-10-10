(function () {
  const content = window.KEREKPARINDEX_CONTENT;
  const sample = window.KEREKPARINDEX_SAMPLE;
  const dialog = document.getElementById("dialog");
  const dialogTitle = document.getElementById("dialog-title");
  const dialogContent = document.getElementById("dialog-content");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const NA = (content && content.naLabel) || "Nincs ellenőrzött adat";
  let lastOpener = null;

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
        out.push("</tbody></table>");
        inTable = false;
      }
    }

    while (i < lines.length) {
      const line = lines[i];
      if (/^\|/.test(line) && lines[i + 1] && /^\|\s*-+/.test(lines[i + 1])) {
        closeUl();
        const headers = line
          .split("|")
          .slice(1, -1)
          .map(function (c) {
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
          const cells = lines[i]
            .split("|")
            .slice(1, -1)
            .map(function (c) {
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
      /\[(.+?)\]\((https?:\/\/[^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>'
    );
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
    if (lastOpener && typeof lastOpener.focus === "function") {
      lastOpener.focus();
    }
    lastOpener = null;
  });

  document.querySelector(".close").addEventListener("click", closeDialog);
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

  function brandByName(name) {
    if (!content) return null;
    const key = String(name).toLocaleLowerCase("hu");
    return content.brands.find(function (b) {
      return (
        b.name.toLocaleLowerCase("hu") === key ||
        b.slug === key ||
        b.id === "brand-" + key
      );
    });
  }

  function brandById(id) {
    return content.brands.find(function (b) {
      return b.id === id;
    });
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
    if (status && status !== "ellenőrzött") bits.push(status);
    (flags || []).forEach(function (f) {
      bits.push(f);
    });
    if (!bits.length) return "";
    return (
      '<p class="meta-line"><span class="badge">' +
      esc(bits.join(" · ")) +
      "</span></p>"
    );
  }

  function renderBrand(brand, opener) {
    const vars = variantsForBrand(brand.id);
    const shops = shopsForBrand(brand.id);
    let html = "";
    html += statusBadge(brand.status, brand.dataFlags);
    html += "<p>" + esc(brand.shortDescription || "") + "</p>";
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
    html += "<h3>Modellváltozatok a próbakörben</h3>";
    if (!vars.length) {
      html +=
        "<p>Ehhez a márkához ebben a próbakörben még nincs közzétett modellváltozat.</p>";
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
      "<p class='note'>" +
      esc(
        "A márka forgalmazása nem bizonyít konkrét modellkészletet vagy kipróbálhatóságot."
      ) +
      "</p>";
    if (!shops.length) {
      html +=
        "<p>Ebben a próbakörben nincs forrással igazolt sells_brand kapcsolat ehhez a márkához.</p>";
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
        ? String(variant.weightKg) +
          (variant.weighingConditions
            ? " (" + variant.weighingConditions + ")"
            : " (mérési feltétel: " + NA + ")")
        : NA);
    let html = statusBadge(variant.status, variant.dataFlags);
    if (brand) {
      html +=
        "<p><button type='button' class='linkish' data-open-brand='" +
        esc(brand.id) +
        "'>" +
        esc(brand.name) +
        "</button></p>";
    }
    html += "<ul class='spec-list'>";
    html += "<li><strong>Típus:</strong> " + esc(val(variant.bikeType)) + "</li>";
    html +=
      "<li><strong>Motor:</strong> " + esc(val(variant.motorExactType)) + "</li>";
    html += "<li><strong>Nyomaték:</strong> " + esc(val(variant.torqueNm)) + (variant.torqueNm != null ? " Nm" : "") + "</li>";
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
        "<p class='note'>Nincs igazolt modell–üzlet készletkapcsolat. Az alábbi üzletek a márkát forgalmazzák (sells_brand).</p>";
      if (!shops.length) {
        html += "<p>" + esc(NA) + " ehhez a márkához a próbakörben.</p>";
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
    }
    show(variant.exactName, html, opener);
    bindDialogNav();
  }

  function renderLocation(loc, opener) {
    const services = (content.servicesByLocation && content.servicesByLocation[loc.id]) || [];
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
    html += "<h3>Szolgáltatások</h3><ul>";
    if (!services.length) {
      html += "<li>" + esc(NA) + " (telephelyi szerep)</li>";
    } else {
      services.forEach(function (s) {
        html +=
          "<li>" +
          esc(s.role) +
          (s.sourceUrl
            ? ' · <a href="' +
              esc(s.sourceUrl) +
              '" target="_blank" rel="noopener">forrás</a>'
            : "") +
          "</li>";
      });
    }
    html += "</ul>";
    html += "<h3>Forgalmazott márkák (igazolt)</h3>";
    html +=
      "<p class='note'>" +
      esc(
        "A márka forgalmazása nem bizonyít konkrét modellkészletet vagy kipróbálhatóságot."
      ) +
      "</p>";
    const links = (loc.brandLinks || []).filter(function (b) {
      return b.inCatalog;
    });
    if (!links.length) {
      html += "<p>Ebben a próbakörben nincs katalógusmárka sells_brand állítás.</p>";
    } else {
      html += "<ul>";
      links.forEach(function (b) {
        html +=
          "<li><button type='button' class='linkish' data-open-brand='" +
          esc(b.brandId) +
          "'>" +
          esc(b.brandName) +
          "</button>" +
          (b.quote ? " — <em>" + esc(b.quote) + "</em>" : "") +
          "</li>";
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
          return s.role === q.role || (q.role === "szerviz" && s.role.indexOf("szerviz") !== -1);
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
      .sort();

    let html =
      "<p>Település, márka vagy szolgáltatás szerint szűrhetsz. A találatok ellenőrzött telephelyek.</p>";
    html += '<form class="place-filter" id="place-filter">';
    html += '<label>Település <select name="city"><option value="">Mind</option>';
    cities.forEach(function (c) {
      html +=
        '<option value="' +
        esc(c) +
        '"' +
        (q.city === c ? " selected" : "") +
        ">" +
        esc(c) +
        "</option>";
    });
    html += "</select></label>";
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
        esc(r) +
        "</option>";
    });
    html += "</select></label>";
    html += '<button type="submit" class="cta">Szűrés ↗</button></form>';
    html += "<p class='meta-line'>" + locs.length + " telephely</p><ul class='place-list'>";
    locs.forEach(function (l) {
      const roles = ((content.servicesByLocation[l.id] || []).map(function (s) {
        return s.role;
      })).join(", ");
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
    }
    bindDialogNav();
  }

  function renderArticle(article, opener) {
    let html = statusBadge(article.status);
    html += mdToHtml(article.bodyMarkdown);
    show(article.title, html, opener);
  }

  function renderExplainers(opener) {
    let html =
      "<p>Hat magyarázó a próbakörből — motor, Nm, Wh, hatótáv, tömeg, szervizháttér.</p><ul>";
    content.explainers.forEach(function (a) {
      html +=
        "<li><button type='button' class='linkish' data-open-explainer='" +
        esc(a.id) +
        "'>" +
        esc(a.title) +
        "</button></li>";
    });
    html += "</ul>";
    show("E-bike magyarázók", html, opener);
    bindDialogNav();
  }

  function renderComparisons(opener) {
    let html =
      "<p>Három összehasonlítás gyártói adatokból. Nincs saját menetpróba és abszolút győztes.</p><ul>";
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
    let html =
      "<p>" +
      esc(content.notice) +
      "</p><div class='dialog-grid'>";
    content.brands.forEach(function (b) {
      html +=
        '<button type="button" class="linkish" data-open-brand="' +
        esc(b.id) +
        '">' +
        esc(b.name) +
        (b.status !== "ellenőrzött" ? " · " + esc(b.status) : "") +
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

  function paintBrandRow() {
    if (!content) return;
    const list = document.querySelector(".brand-list");
    if (!list) return;
    list.innerHTML = "";
    content.brands.forEach(function (b) {
      const btn = document.createElement("button");
      btn.className = "brand";
      btn.type = "button";
      btn.dataset.brand = b.name;
      btn.dataset.brandId = b.id;
      btn.textContent = b.name;
      if (b.status === "előkészített") {
        btn.title = "Előkészített státusz";
      }
      btn.addEventListener("click", function () {
        renderBrand(b, btn);
      });
      list.appendChild(btn);
    });
  }

  if (content) {
    paintBrandRow();
  } else {
    document.querySelectorAll("[data-brand]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        show(
          btn.dataset.brand,
          "<p>A tartalmi csomag nem töltődött be.</p>",
          btn
        );
      });
    });
  }

  document.getElementById("all-brands").addEventListener("click", function () {
    if (content) renderAllBrands(this);
  });

  document.querySelectorAll("[data-category]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (btn.dataset.scrollTo) {
        document
          .getElementById(btn.dataset.scrollTo)
          .scrollIntoView({ behavior: scrollBehavior() });
        return;
      }
      const cat = btn.dataset.category;
      if (!content) return;
      if (cat === "Kerékpárok") {
        renderAllBrands(btn);
        return;
      }
      if (cat === "Üzletek") {
        renderPlaces({ role: "eladas" }, btn);
        return;
      }
      if (cat === "Szervizek") {
        renderPlaces({ role: "szerviz" }, btn);
        return;
      }
      if (cat === "Alkatrészek" || cat === "Felszerelések") {
        show(
          cat,
          "<p>Ebben a próbakörben még nincs önálló alkatrész-/felszereléskatalogus. Az e-bike magyarázók és modelladatlapok az Elektromos szekcióban érhetők el.</p>",
          btn
        );
        return;
      }
      show(cat, "<p>" + esc(NA) + "</p>", btn);
    });
  });

  const metricTabs = Array.prototype.slice.call(
    document.querySelectorAll("[data-metric]")
  );
  const explanation = document.getElementById("explanation");

  const metricMap = {
    wh: "art-exp-wh",
    nm: "art-exp-nm",
    km: "art-exp-range",
  };

  function activateMetric(btn, focusTab) {
    metricTabs.forEach(function (tab) {
      const active = tab === btn;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    let title = sample.metrics[btn.dataset.metric].title;
    let body = sample.metrics[btn.dataset.metric].body;
    if (content) {
      const art = content.explainers.find(function (a) {
        return a.id === metricMap[btn.dataset.metric];
      });
      if (art) {
        title = art.title;
        body =
          " Röviden: kattints a Bemutatók gombra a teljes magyarázóhoz. " +
          art.bodyMarkdown
            .split("\n")
            .filter(function (l) {
              return l && !l.startsWith("#") && !l.startsWith("-") && !l.startsWith("|");
            })
            .slice(0, 2)
            .join(" ");
      }
    }
    explanation.setAttribute("aria-labelledby", btn.id);
    explanation.innerHTML = "<strong>" + esc(title) + "</strong> " + esc(body);
    if (focusTab) btn.focus();
  }

  metricTabs.forEach(function (btn, index) {
    btn.addEventListener("click", function () {
      activateMetric(btn, false);
    });
    btn.addEventListener("keydown", function (e) {
      let next = null;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        next = metricTabs[(index + 1) % metricTabs.length];
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        next = metricTabs[(index - 1 + metricTabs.length) % metricTabs.length];
      } else if (e.key === "Home") {
        next = metricTabs[0];
      } else if (e.key === "End") {
        next = metricTabs[metricTabs.length - 1];
      }
      if (!next) return;
      e.preventDefault();
      activateMetric(next, true);
    });
  });

  document.querySelectorAll("[data-editorial]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const key = btn.dataset.editorial;
      if (!content) return;
      if (key === "500 vagy 750 Wh?") {
        const a = content.explainers.find(function (x) {
          return x.id === "art-exp-wh";
        });
        if (a) return renderArticle(a, btn);
      }
      if (key === "Mitől drágább egy e-bike?") {
        return renderComparisons(btn);
      }
      if (key === "E-bike-bemutatók") {
        return renderExplainers(btn);
      }
      if (key === "E-bike-összehasonlítások") {
        return renderComparisons(btn);
      }
      if (key === "Jó vételt keresel?" || key === "Elektromoskerékpár-akciók") {
        return show(
          key,
          "<p>Ebben a próbakörben nincs élő akciós / áras adatbázis. Az ellenőrzött üzletek a helykeresőben érhetők el.</p>",
          btn
        );
      }
      show(key, "<p>" + esc(NA) + "</p>", btn);
    });
  });

  document.getElementById("local").addEventListener("click", function () {
    if (content) renderPlaces({}, this);
  });

  function norm(s) {
    return s
      .toLocaleLowerCase("hu")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function applySearch(qRaw) {
    const q = norm(qRaw.trim());
    const message = document.getElementById("search-message");
    if (!content) {
      message.hidden = false;
      message.textContent = "A tartalmi csomag nem töltődött be.";
      return;
    }
    if (!q) {
      message.hidden = true;
      message.textContent = "";
      document.querySelectorAll("[data-brand], [data-category]").forEach(function (el) {
        el.hidden = false;
      });
      return;
    }

    const hits = [];
    content.brands.forEach(function (b) {
      if (norm(b.name).includes(q) || norm(b.shortDescription || "").includes(q)) {
        hits.push({ type: "Márka", label: b.name, open: function () { renderBrand(b); } });
      }
    });
    content.variants.forEach(function (v) {
      if (norm(v.exactName).includes(q) || norm(v.motorExactType || "").includes(q)) {
        hits.push({ type: "Modell", label: v.exactName, open: function () { renderVariant(v); } });
      }
    });
    content.locations.forEach(function (l) {
      const city = (l.address || {}).city || "";
      if (norm(l.name).includes(q) || norm(city).includes(q)) {
        hits.push({ type: "Üzlet", label: l.name + " · " + city, open: function () { renderLocation(l); } });
      }
    });
    content.explainers.concat(content.comparisons).forEach(function (a) {
      if (norm(a.title).includes(q)) {
        hits.push({ type: "Cikk", label: a.title, open: function () { renderArticle(a); } });
      }
    });

    document.querySelectorAll("[data-brand], [data-category]").forEach(function (el) {
      const yes = !q || norm(el.textContent).includes(q);
      el.hidden = !yes;
    });

    message.hidden = false;
    if (!hits.length) {
      message.textContent =
        "Nincs egyezés. Próbáld: CUBE, Trek, Debrecen, szerviz, hatótáv vagy összehasonlítás.";
      return;
    }
    message.innerHTML =
      hits.length +
      " találat. " +
      hits
        .slice(0, 8)
        .map(function (h, idx) {
          return (
            '<button type="button" class="linkish" data-hit="' +
            idx +
            '">' +
            esc(h.type) +
            ": " +
            esc(h.label) +
            "</button>"
          );
        })
        .join(" · ");
    message.querySelectorAll("[data-hit]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        hits[Number(btn.getAttribute("data-hit"))].open();
      });
    });
  }

  document.getElementById("search").addEventListener("submit", function (e) {
    e.preventDefault();
    applySearch(document.getElementById("query").value);
  });

  document.getElementById("query").addEventListener("input", function (e) {
    if (!e.target.value) {
      document
        .querySelectorAll("[data-brand], [data-category]")
        .forEach(function (b) {
          b.hidden = false;
        });
      document.getElementById("search-message").hidden = true;
    }
  });

  const searchIcon = document.querySelector(".search-icon");
  if (searchIcon) {
    searchIcon.addEventListener("click", function () {
      document.getElementById("query").focus();
      document
        .getElementById("search")
        .scrollIntoView({ behavior: scrollBehavior(), block: "center" });
    });
  }

  const menu = document.querySelector(".menu-toggle");
  const nav = document.getElementById("main-nav");

  function closeMenu() {
    nav.classList.remove("open");
    menu.setAttribute("aria-expanded", "false");
    menu.setAttribute("aria-label", "Menü megnyitása");
  }

  menu.addEventListener("click", function () {
    const open = nav.classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute(
      "aria-label",
      open ? "Menü bezárása" : "Menü megnyitása"
    );
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

  // Deep links: #marka-cube, #modell-..., #uzlet-..., #cikk-...
  function routeHash() {
    if (!content) return;
    const h = (location.hash || "").replace(/^#/, "");
    if (!h) return;
    if (h === "markak") return renderAllBrands();
    if (h === "helyek") return renderPlaces({});
    if (h.indexOf("marka-") === 0) {
      const slug = h.slice(6);
      const b = content.brands.find(function (x) {
        return x.slug === slug || x.id === "brand-" + slug;
      });
      if (b) renderBrand(b);
    } else if (h.indexOf("modell-") === 0) {
      const id = h.slice(7);
      const v = content.variants.find(function (x) {
        return x.id === id || x.id === "var-" + id;
      });
      if (v) renderVariant(v);
    } else if (h.indexOf("uzlet-") === 0) {
      const id = h.slice(6);
      const loc = content.locations.find(function (x) {
        return x.id === id || x.id === "loc-" + id;
      });
      if (loc) renderLocation(loc);
    } else if (h.indexOf("cikk-") === 0) {
      const slug = h.slice(5);
      const a = content.explainers
        .concat(content.comparisons)
        .find(function (x) {
          return x.slug === slug || x.id === slug;
        });
      if (a) renderArticle(a);
    }
  }
  window.addEventListener("hashchange", routeHash);
  routeHash();
})();
