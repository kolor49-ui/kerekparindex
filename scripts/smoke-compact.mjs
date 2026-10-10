/**
 * ORBIT Compact smoke — puppeteer-core + system Chrome.
 * Run from a temp dir with puppeteer-core installed, or with NODE_PATH set.
 *
 * Example:
 *   TMP=$(mktemp -d) && cd "$TMP" && npm i --no-fund --no-audit puppeteer-core@23.11.1
 *   node /path/to/scripts/smoke-compact.mjs
 */
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT =
  process.env.PROJECT_ROOT ||
  path.resolve(__dirname, "..");
const BASE = process.env.BASE_URL || "http://127.0.0.1:8765/";
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const SHOT_DIR = path.join(PROJECT, "screenshots");
const SECTION_ORDER = [
  "markak",
  "search",
  "felfedezes",
  "aktualis",
  "elektromos",
  "helyek",
];
const VIEWPORTS = [
  { w: 360, h: 900, key: "360" },
  { w: 390, h: 900, key: "390" },
  { w: 768, h: 1100, key: "768" },
  { w: 1024, h: 900, key: "1024" },
  { w: 1440, h: 900, key: "1440" },
];

function fail(msg, extra) {
  return { pass: false, error: msg, ...extra };
}

async function measureH1(page) {
  return page.evaluate(() => {
    const h1 = document.querySelector("h1");
    const text = h1 ? h1.textContent.replace(/\s+/g, " ").trim() : "";
    const includesFullWord = text.includes("Magyarországon.");
    const cs = h1 ? getComputedStyle(h1) : null;
    const fontSize = cs ? cs.fontSize : null;
    const fontSizePx = fontSize ? parseFloat(fontSize) : null;

    let wordRight = null;
    let wordWithinViewport = false;
    if (h1 && includesFullWord) {
      const full = h1.textContent;
      const idx = full.indexOf("Magyarországon.");
      const range = document.createRange();
      // Walk text nodes to set range on the word
      const walker = document.createTreeWalker(h1, NodeFilter.SHOW_TEXT);
      let pos = 0;
      let startNode = null;
      let startOffset = 0;
      let endNode = null;
      let endOffset = 0;
      const targetStart = idx;
      const targetEnd = idx + "Magyarországon.".length;
      while (walker.nextNode()) {
        const n = walker.currentNode;
        const len = n.textContent.length;
        if (!startNode && pos + len > targetStart) {
          startNode = n;
          startOffset = targetStart - pos;
        }
        if (startNode && !endNode && pos + len >= targetEnd) {
          endNode = n;
          endOffset = targetEnd - pos;
          break;
        }
        pos += len;
      }
      if (startNode && endNode) {
        range.setStart(startNode, startOffset);
        range.setEnd(endNode, endOffset);
        const rects = range.getClientRects();
        if (rects.length) {
          const last = rects[rects.length - 1];
          wordRight = last.right;
          wordWithinViewport = last.right < window.innerWidth - 2;
        }
      }
    }

    return {
      text,
      includesFullWord,
      fontSize,
      fontSizePx,
      wordRight,
      wordWithinViewport,
      innerWidth: window.innerWidth,
    };
  });
}

async function assertSectionOrder(page) {
  return page.evaluate((ids) => {
    const tops = ids.map((id) => {
      const el = document.getElementById(id);
      if (!el) return { id, top: null, missing: true };
      return { id, top: el.getBoundingClientRect().top + window.scrollY, missing: false };
    });
    const missing = tops.filter((t) => t.missing).map((t) => t.id);
    let ordered = missing.length === 0;
    for (let i = 1; i < tops.length; i++) {
      if (tops[i].top < tops[i - 1].top) ordered = false;
    }
    return { ordered, tops, missing };
  }, SECTION_ORDER);
}

async function testMobileNav(page) {
  return page.evaluate(async () => {
    const menu = document.querySelector(".menu-toggle");
    const nav = document.getElementById("main-nav");
    const style = menu ? getComputedStyle(menu) : null;
    const visible =
      !!menu &&
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      menu.offsetParent !== null;

    const result = {
      menuVisible: visible,
      opened: false,
      closedByEscape: false,
      linkCount: 0,
      links: [],
      ariaExpandedOpen: null,
      ariaExpandedClosed: null,
      hasOpenClass: false,
    };

    if (!visible) return result;

    menu.click();
    result.hasOpenClass = nav.classList.contains("open");
    result.ariaExpandedOpen = menu.getAttribute("aria-expanded");
    result.opened =
      result.hasOpenClass && result.ariaExpandedOpen === "true";

    const anchors = Array.from(nav.querySelectorAll("a"));
    result.links = anchors.map((a) => a.textContent.trim());
    result.linkCount = anchors.length;

    document.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Escape", bubbles: true })
    );
    result.closedByEscape =
      !nav.classList.contains("open") &&
      menu.getAttribute("aria-expanded") === "false";
    result.ariaExpandedClosed = menu.getAttribute("aria-expanded");

    return result;
  });
}

async function testSearch(page) {
  return page.evaluate(async () => {
    const input = document.getElementById("query");
    const form = document.getElementById("search");
    input.focus();
    input.value = "";
    input.dispatchEvent(new Event("input", { bubbles: true }));

    input.value = "elektromos";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    form.dispatchEvent(
      new Event("submit", { bubbles: true, cancelable: true })
    );
    // submit handler is on form via addEventListener — need requestSubmit
    return null;
  }).then(async () => {
    await page.$eval("#query", (el) => {
      el.value = "elektromos";
    });
    await page.$eval("#search", (form) => {
      form.requestSubmit();
    });
    await new Promise((r) => setTimeout(r, 80));

    const afterSubmit = await page.evaluate(() => {
      const cats = Array.from(
        document.querySelectorAll("[data-category]:not([hidden])")
      ).map((el) => el.dataset.category);
      return {
        visibleCats: cats,
        includesElektromos: cats.includes("Elektromos"),
      };
    });

    await page.$eval("#query", (el) => {
      el.value = "";
      el.dispatchEvent(new Event("input", { bubbles: true }));
    });
    await new Promise((r) => setTimeout(r, 80));

    const afterClear = await page.evaluate(() => {
      const all = document.querySelectorAll("[data-brand], [data-category]");
      const hidden = Array.from(all).filter((el) => el.hidden).length;
      return {
        restored: hidden === 0,
        total: all.length,
        hidden,
      };
    });

    return {
      ...afterSubmit,
      ...afterClear,
      pass: afterSubmit.includesElektromos && afterClear.restored,
    };
  });
}

async function testMetrics(page) {
  return page.evaluate(() => {
    const tablist = document.querySelector('[role="tablist"]');
    const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
    const tabpanel = document.querySelector('[role="tabpanel"]');
    const pressed = document.querySelectorAll("[aria-pressed]");
    const explanation = document.getElementById("explanation");
    const before = explanation ? explanation.innerHTML : "";

    const rolesOk = !!tablist && tabs.length >= 3 && !!tabpanel;
    const noAriaPressed = pressed.length === 0;

    const wh = document.querySelector('[data-metric="wh"]');
    const nm = document.querySelector('[data-metric="nm"]');
    if (wh) wh.focus();
    wh?.dispatchEvent(
      new KeyboardEvent("keydown", {
        key: "ArrowRight",
        bubbles: true,
        cancelable: true,
      })
    );

    const nmSelected = nm?.getAttribute("aria-selected") === "true";
    const after = explanation ? explanation.innerHTML : "";
    const explanationUpdated = after !== before && after.length > 0;

    return {
      rolesOk,
      noAriaPressed,
      nmSelected,
      explanationUpdated,
      beforeLen: before.length,
      afterLen: after.length,
      pass: rolesOk && noAriaPressed && nmSelected && explanationUpdated,
    };
  });
}

async function testDialog(page) {
  // Click CUBE brand button
  await page.evaluate(() => {
    const cube = document.querySelector('[data-brand="CUBE"]');
    if (cube) cube.click();
  });
  await new Promise((r) => setTimeout(r, 120));

  const opened = await page.evaluate(() => {
    const d = document.getElementById("dialog");
    return !!(d && d.open);
  });

  await page.keyboard.press("Escape");
  await new Promise((r) => setTimeout(r, 120));

  const after = await page.evaluate(() => {
    const d = document.getElementById("dialog");
    const active = document.activeElement;
    return {
      closed: d && !d.open,
      focusTag: active?.tagName,
      focusText: (active?.textContent || "").trim(),
      focusIsCube:
        active?.getAttribute?.("data-brand") === "CUBE" ||
        (active?.textContent || "").trim() === "CUBE",
    };
  });

  return {
    opened,
    ...after,
    pass: opened && after.closed && after.focusIsCube,
  };
}

async function desktopHeroArt(page) {
  return page.evaluate(() => {
    const art = document.querySelector(".hero-art");
    if (!art) return { present: false, display: null, pass: false };
    const display = getComputedStyle(art).display;
    return {
      present: true,
      display,
      pass: display !== "none",
    };
  });
}

async function run() {
  fs.mkdirSync(SHOT_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: ["--hide-scrollbars", "--disable-gpu"],
    defaultViewport: null,
  });

  const results = {
    date: "2026-10-10",
    baseUrl: BASE,
    chrome: CHROME,
    pass: true,
    viewports: {},
    sectionOrder: {},
    h1: {},
    mobileNav: {},
    search: null,
    metrics: null,
    dialog: null,
    desktop: {},
    screenshots: [],
    errors: [],
  };

  try {
    const page = await browser.newPage();
    await page.setCacheEnabled(false);

    for (const vp of VIEWPORTS) {
      await page.setViewport({ width: vp.w, height: vp.h, deviceScaleFactor: 1 });
      await page.goto(BASE + "?cb=compact-" + Date.now() + "-" + vp.key, {
        waitUntil: "networkidle0",
        timeout: 30000,
      });

      const shotName = `compact-${vp.key}.png`;
      const shotPath = path.join(SHOT_DIR, shotName);
      await page.screenshot({ path: shotPath, fullPage: true });
      results.screenshots.push(shotName);

      const order = await assertSectionOrder(page);
      results.sectionOrder[vp.key] = order;
      if (!order.ordered) {
        results.pass = false;
        results.errors.push(`sectionOrder ${vp.key}`);
      }

      const h1 = await measureH1(page);
      results.h1[vp.key] = h1;
      if (!h1.includesFullWord || !h1.wordWithinViewport) {
        results.pass = false;
        results.errors.push(`h1 ${vp.key}`);
      }

      if (vp.key === "360" || vp.key === "390") {
        const nav = await testMobileNav(page);
        results.mobileNav[vp.key] = nav;
        const navOk =
          nav.menuVisible &&
          nav.opened &&
          nav.closedByEscape &&
          nav.linkCount === 5;
        if (!navOk) {
          results.pass = false;
          results.errors.push(`mobileNav ${vp.key}`);
        }
      }

      results.viewports[vp.key] = {
        width: vp.w,
        height: vp.h,
        h1FontSize: h1.fontSize,
        h1FontSizePx: h1.fontSizePx,
      };
    }

    // Interaction tests at 390 (mobile-capable + metrics visible)
    await page.setViewport({ width: 390, height: 900, deviceScaleFactor: 1 });
    await page.goto(BASE + "?cb=interact-" + Date.now(), {
      waitUntil: "networkidle0",
      timeout: 30000,
    });

    results.search = await testSearch(page);
    if (!results.search.pass) {
      results.pass = false;
      results.errors.push("search");
    }

    results.metrics = await testMetrics(page);
    if (!results.metrics.pass) {
      results.pass = false;
      results.errors.push("metrics");
    }

    results.dialog = await testDialog(page);
    if (!results.dialog.pass) {
      results.pass = false;
      results.errors.push("dialog");
    }

    // Desktop 1440 checks
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 1 });
    await page.goto(BASE + "?cb=desktop-" + Date.now(), {
      waitUntil: "networkidle0",
      timeout: 30000,
    });
    const art = await desktopHeroArt(page);
    const h1d = await measureH1(page);
    const fontOk =
      h1d.fontSizePx != null &&
      h1d.fontSizePx >= 30 &&
      h1d.fontSizePx <= 44 &&
      h1d.fontSizePx < 70;
    results.desktop = {
      heroArt: art,
      h1FontSize: h1d.fontSize,
      h1FontSizePx: h1d.fontSizePx,
      compactFontSize: fontOk,
      pass: art.pass && fontOk,
    };
    if (!results.desktop.pass) {
      results.pass = false;
      results.errors.push("desktop");
    }

    results.summary = {
      pass: results.pass,
      h1FontSizes: Object.fromEntries(
        Object.entries(results.h1).map(([k, v]) => [k, v.fontSize])
      ),
      sectionOrderOk: Object.values(results.sectionOrder).every((s) => s.ordered),
      mobileNavOk: ["360", "390"].every(
        (k) =>
          results.mobileNav[k]?.menuVisible &&
          results.mobileNav[k]?.opened &&
          results.mobileNav[k]?.closedByEscape &&
          results.mobileNav[k]?.linkCount === 5
      ),
      searchOk: !!results.search?.pass,
      metricsOk: !!results.metrics?.pass,
      dialogOk: !!results.dialog?.pass,
      desktopOk: !!results.desktop?.pass,
      liveDeployAvoided: true,
    };
  } catch (err) {
    results.pass = false;
    results.errors.push(String(err && err.stack ? err.stack : err));
  } finally {
    await browser.close();
  }

  const outJson = path.join(PROJECT, "TEST-RUN-RESULT.json");
  fs.writeFileSync(outJson, JSON.stringify(results, null, 2) + "\n");
  console.log(JSON.stringify(results, null, 2));
  process.exit(results.pass ? 0 : 1);
}

run();
