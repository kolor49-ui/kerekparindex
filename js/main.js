(function () {
  const sample = window.KEREKPARINDEX_SAMPLE;
  const dialog = document.getElementById("dialog");
  const dialogTitle = document.getElementById("dialog-title");
  const dialogContent = document.getElementById("dialog-content");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let lastOpener = null;

  function scrollBehavior() {
    return reduceMotion.matches ? "auto" : "smooth";
  }

  function grid(items) {
    return (
      '<div class="dialog-grid">' +
      items.map((item) => "<span>" + item + "</span>").join("") +
      "</div>"
    );
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

  document.querySelectorAll("[data-brand]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      show(
        btn.dataset.brand,
        "<p>A márka saját oldala összekötheti a kínálatot, a bemutatókat és a hazai vásárlási lehetőségeket.</p>" +
          grid(sample.dialogPaths) +
          "<p>Ez a márkaoldal tervezett felépítése. Ellenőrzött adatokkal a következő szakaszban tölthető fel.</p>",
        btn
      );
    });
  });

  document.getElementById("all-brands").addEventListener("click", function () {
    show(
      "A márkák világa",
      "<p>Kerékpár-, alkatrész- és felszerelésmárkák egy közös, kereshető rendszerben.</p>" +
        grid(sample.dialogPaths),
      this
    );
  });

  document.querySelectorAll("[data-category]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (btn.dataset.scrollTo) {
        document
          .getElementById(btn.dataset.scrollTo)
          .scrollIntoView({ behavior: scrollBehavior() });
        return;
      }
      show(
        btn.dataset.category,
        "<p>A kategória oldalán márkák, bemutatók, vásárlási lehetőségek és kapcsolódó szolgáltatások találkoznak.</p>" +
          grid(sample.dialogPaths) +
          "<p>A látványterv a szerkezetet mutatja; élő katalógust még nem tartalmaz.</p>",
        btn
      );
    });
  });

  const metricTabs = Array.prototype.slice.call(
    document.querySelectorAll("[data-metric]")
  );
  const explanation = document.getElementById("explanation");

  function activateMetric(btn, focusTab) {
    metricTabs.forEach(function (tab) {
      const active = tab === btn;
      tab.classList.toggle("active", active);
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    const metric = sample.metrics[btn.dataset.metric];
    explanation.setAttribute("aria-labelledby", btn.id);
    explanation.innerHTML =
      "<strong>" + metric.title + "</strong>" + metric.body;
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
      const title = btn.dataset.editorial;
      const custom = sample.editorialBodies[title];
      const body =
        custom ||
        "<p>Itt önálló szerkesztett tartalmak jelennek majd meg: érthető magyarázatokkal, ellenőrzött forrásokkal és a kapcsolódó kereskedők elérhetőségével.</p><p>Ez egy tartalmi belépő látványterve, nem élő ajánlat vagy megjelent teszt.</p>";
      show(title, body, btn);
    });
  });

  document.getElementById("local").addEventListener("click", function () {
    show(
      "Találd meg a helyed.",
      "<p>Az országos keresőben település, márka és szolgáltatás alapján lehet majd üzletet vagy szervizt választani.</p>" +
        grid(sample.localServices) +
        "<p>A látványterv még nem tartalmaz ellenőrzött üzletadatokat.</p>",
      this
    );
  });

  function norm(s) {
    return s
      .toLocaleLowerCase("hu")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function applySearch(qRaw) {
    const q = norm(qRaw.trim());
    let n = 0;
    document.querySelectorAll("[data-brand], [data-category]").forEach(function (el) {
      const yes = !q || norm(el.textContent).includes(q);
      el.hidden = !yes;
      if (yes) n += 1;
    });
    const message = document.getElementById("search-message");
    if (!q) {
      message.hidden = true;
      message.textContent = "";
      return;
    }
    message.hidden = false;
    message.textContent = n
      ? n + " márka vagy kategória a helyi mintában."
      : "Nincs egyezés a mintában. Próbáld: Cube, elektromos, alkatrészek vagy szerviz.";
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
})();
