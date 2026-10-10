/**
 * Regression: hero search must return published places for city queries
 * on the default Termékek tab (not only on Helyek).
 *
 * Usage:
 *   python3 -m http.server 8765
 *   node scripts/test-hero-city-search.mjs
 *   BASE_URL=https://kerekparindex.hu/ node scripts/test-hero-city-search.mjs
 */
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT = path.resolve(__dirname, "..");
const BASE = process.env.BASE_URL || "http://127.0.0.1:8765/";
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const OUT = path.join(PROJECT, "TEST-HERO-CITY-SEARCH.json");

function expectCityCount(content, city) {
  return (content.locations || []).filter(
    (l) => ((l.address || {}).city || "") === city
  ).length;
}

async function activateTab(page, tab) {
  await page.evaluate((t) => {
    const el = document.querySelector(`[data-search="${t}"]`);
    if (el) el.click();
  }, tab);
  await page.waitForFunction(
    (t) =>
      document.querySelector(`[data-search="${t}"]`)?.getAttribute("aria-pressed") ===
      "true",
    { timeout: 4000 },
    tab
  );
}

async function searchHero(page, query, { viaEnter = false, tab = null } = {}) {
  await activateTab(page, tab || "termek");
  await page.$eval("#query", (el) => {
    el.value = "";
  });
  await page.type("#query", query, { delay: 8 });
  if (viaEnter) {
    await page.focus("#query");
    await page.keyboard.press("Enter");
  } else {
    await page.click("#search button.go");
  }
  await page.waitForFunction(
    () => {
      const panel = document.getElementById("results");
      const msg = document.getElementById("search-message");
      return (
        (panel && !panel.hidden) ||
        (msg && !msg.hidden && /nincs egyezés|találat/i.test(msg.textContent || ""))
      );
    },
    { timeout: 8000 }
  );
  return page.evaluate(() => {
    const panel = document.getElementById("results");
    const msg = document.getElementById("search-message");
    const cards = panel && !panel.hidden
      ? [...panel.querySelectorAll(".result")].map((el) => ({
          type: (el.querySelector("small") || {}).textContent || "",
          label: (el.querySelector("h3") || {}).textContent || "",
          sub: (el.querySelector("p") || {}).textContent || "",
        }))
      : [];
    const placeCards = cards.filter((c) => /üzlet/i.test(c.type));
    return {
      panelVisible: !!(panel && !panel.hidden),
      message: (msg && !msg.hidden ? msg.textContent : "") || "",
      status: (document.getElementById("result-status") || {}).textContent || "",
      cardCount: cards.length,
      placeCardCount: placeCards.length,
      placeLabels: placeCards.map((c) => c.label),
      activeTab: (
        document.querySelector('.search-tabs [aria-pressed="true"]') || {}
      ).dataset?.search,
    };
  });
}

async function runViewport(browser, width, height) {
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.goto(BASE, { waitUntil: "networkidle0", timeout: 60000 });
  const content = await page.evaluate(() => window.KEREKPARINDEX_CONTENT);
  if (!content || !content.locations || !content.locations.length) {
    throw new Error("KEREKPARINDEX_CONTENT.locations missing");
  }

  const cases = [];
  const cities = ["Szolnok", "Debrecen", "Győr"];
  for (const city of cities) {
    const published = expectCityCount(content, city);
    const exact = await searchHero(page, city, { viaEnter: false });
    cases.push({
      id: `default-tab-exact-${city}`,
      query: city,
      publishedInCity: published,
      placeCardCount: exact.placeCardCount,
      status: exact.status,
      pass:
        exact.panelVisible &&
        published > 0 &&
        exact.placeCardCount >= Math.min(published, 24) &&
        // status reports full hit count; cards may be capped at 24
        /találat/i.test(exact.status || exact.message),
    });

    const ascii = city.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const folded = await searchHero(page, ascii.toLowerCase(), { viaEnter: true });
    cases.push({
      id: `default-tab-ascii-enter-${ascii}`,
      query: ascii.toLowerCase(),
      publishedInCity: published,
      placeCardCount: folded.placeCardCount,
      pass: folded.panelVisible && folded.placeCardCount > 0,
    });
  }

  // Partial + whitespace
  const partial = await searchHero(page, "  szoln  ", { viaEnter: false });
  cases.push({
    id: "default-tab-partial-whitespace",
    query: "  szoln  ",
    placeCardCount: partial.placeCardCount,
    pass: partial.panelVisible && partial.placeCardCount >= expectCityCount(content, "Szolnok"),
  });

  // Helyek tab still works
  const hely = await searchHero(page, "Miskolc", { tab: "hely", viaEnter: true });
  cases.push({
    id: "hely-tab-miskolc",
    query: "Miskolc",
    publishedInCity: expectCityCount(content, "Miskolc"),
    placeCardCount: hely.placeCardCount,
    pass:
      hely.activeTab === "hely" &&
      hely.placeCardCount === expectCityCount(content, "Miskolc"),
  });

  // Brand search still works on default tab
  const brand = await searchHero(page, "Trek", { tab: "termek" });
  cases.push({
    id: "default-tab-brand-trek",
    query: "Trek",
    cardCount: brand.cardCount,
    pass: brand.panelVisible && brand.cardCount > 0,
  });

  // Nonsense → no false place flood
  const miss = await searchHero(page, "xyzzyqwerty999", { tab: "termek" });
  cases.push({
    id: "default-tab-miss",
    query: "xyzzyqwerty999",
    pass: !miss.panelVisible && /nincs egyezés/i.test(miss.message),
  });

  await page.close();
  return {
    viewport: `${width}x${height}`,
    cases,
    pass: cases.every((c) => c.pass),
  };
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu"],
  });
  const report = {
    accessedAt: new Date().toISOString(),
    base: BASE,
    pass: true,
    viewports: [],
  };
  try {
    for (const vp of [
      { w: 390, h: 844 },
      { w: 1280, h: 800 },
    ]) {
      const r = await runViewport(browser, vp.w, vp.h);
      report.viewports.push(r);
      if (!r.pass) report.pass = false;
    }
  } finally {
    await browser.close();
  }
  fs.writeFileSync(OUT, JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify({ pass: report.pass, out: OUT, viewports: report.viewports.map((v) => ({ viewport: v.viewport, pass: v.pass, fails: v.cases.filter((c) => !c.pass).map((c) => c.id) })) }, null, 2));
  if (!report.pass) process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
