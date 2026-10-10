/**
 * ORBIT Világ viewport smoke + screenshots.
 */
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT = process.env.PROJECT_ROOT || path.resolve(__dirname, "..");
const BASE = process.env.BASE_URL || "http://127.0.0.1:8765/";
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const SHOT_DIR = path.join(PROJECT, "screenshots", "orbit-vilag");

const VIEWPORTS = [
  { w: 360, h: 900, key: "360" },
  { w: 390, h: 900, key: "390" },
  { w: 768, h: 1100, key: "768" },
  { w: 1024, h: 900, key: "1024" },
  { w: 1440, h: 900, key: "1440" },
];

async function measure(page) {
  return page.evaluate(() => {
    const issues = [];
    if (document.querySelector(".demo")) issues.push("demo_bar_present");

    const gateways = [...document.querySelectorAll(".gateways .gateway")].filter(
      (el) => !el.hidden && getComputedStyle(el).display !== "none"
    );
    if (gateways.length !== 6) issues.push("gateway_count:" + gateways.length);
    const chips = [...document.querySelectorAll(".search-tabs .chip")].filter(
      (el) => getComputedStyle(el).display !== "none"
    );
    if (chips.length !== 5) issues.push("chip_count:" + chips.length);
    const brandLabels = [...document.querySelectorAll(".brands .brand")].map((b) =>
      b.textContent.trim()
    );
    if (brandLabels.join("|") !== "CUBE|TREK|GIANT|GEPIDA|SPECIALIZED|MERIDA")
      issues.push("brand_order:" + brandLabels.join("|"));

    const icons = gateways.map((g) => {
      const icon = g.querySelector(".icon");
      const r = icon ? icon.getBoundingClientRect() : null;
      return r ? { w: Math.round(r.width), h: Math.round(r.height) } : null;
    });

    const brandEls = [...document.querySelectorAll(".brands .brand")];
    const brandOverflow = brandEls.some((b) => {
      const r = b.getBoundingClientRect();
      return r.right > window.innerWidth + 1;
    });
    if (brandOverflow) issues.push("brand_overflow");

    const search = document.querySelector(".search-row");
    const searchRect = search ? search.getBoundingClientRect() : null;
    if (searchRect && searchRect.width > window.innerWidth) issues.push("search_overflow");

    if (document.querySelector(".planned-panel")) issues.push("planned_panel_present");
    const routes = [...document.querySelectorAll(".routes .route")];
    if (routes.length !== 2) issues.push("route_count:" + routes.length);
    const events = [...document.querySelectorAll("#esemenyek .event")];
    if (events.length !== 3) issues.push("event_count:" + events.length);
    const used = [...document.querySelectorAll(".used-grid .used")].filter(
      (el) => getComputedStyle(el).display !== "none"
    );
    const expectUsed = window.innerWidth <= 1000 && window.innerWidth > 650 ? 2 : 3;
    if (used.length !== expectUsed) issues.push("used_count:" + used.length);
    if (!document.getElementById("country")) issues.push("country_select_missing");
    if (!document.querySelector("#landscape")) issues.push("landscape_symbol_missing");
    const bodyText = document.body.innerText;
    if (/Kitalált/.test(bodyText)) issues.push("kitalalt_copy_visible");
    if (!/Hamarosan/.test(bodyText)) issues.push("hamarosan_missing");

    // open a brand dialog if possible
    return {
      issues,
      icons,
      gatewayCount: gateways.length,
      brandCount: brandEls.length,
      routeCount: routes.length,
      eventCount: events.length,
      usedCount: used.length,
      h1: (document.querySelector("h1") || {}).textContent || "",
      hasContent: !!window.KEREKPARINDEX_CONTENT,
      contentBrands: window.KEREKPARINDEX_CONTENT
        ? window.KEREKPARINDEX_CONTENT.brands.length
        : 0,
      width: window.innerWidth,
    };
  });
}

async function fullPageShot(page, name) {
  const file = path.join(SHOT_DIR, name);
  await page.screenshot({ path: file, fullPage: true });
  return file;
}

async function main() {
  fs.mkdirSync(SHOT_DIR, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu"],
  });
  const page = await browser.newPage();
  const results = { pass: true, viewports: [], shots: [], checks: [] };

  for (const vp of VIEWPORTS) {
    await page.setViewport({ width: vp.w, height: vp.h, deviceScaleFactor: 1 });
    await page.goto(BASE, { waitUntil: "networkidle0", timeout: 60000 });
    const m = await measure(page);
    const shot = await fullPageShot(page, `vilag-${vp.key}.png`);

    // Icon size expectations
    const desktop = vp.w >= 651;
    let iconOk = true;
    if (desktop) {
      iconOk = m.icons.every((i) => i && i.w >= 20 && i.w <= 28 && i.h >= 20 && i.h <= 28);
      if (!iconOk) m.issues.push("desktop_icon_size:" + JSON.stringify(m.icons));
    } else {
      iconOk = m.icons.every((i) => i && i.w >= 20 && i.w <= 32);
      if (!iconOk) m.issues.push("mobile_icon_size:" + JSON.stringify(m.icons));
    }

    // Open brand + places briefly
    await page.click(".brands .brand");
    await page.waitForSelector("dialog[open]", { timeout: 5000 }).catch(() => null);
    const dialogOpen = await page.evaluate(() => {
      const d = document.querySelector("dialog");
      return !!(d && d.open);
    });
    if (!dialogOpen) m.issues.push("brand_dialog_failed");
    await page.keyboard.press("Escape");
    await new Promise((r) => setTimeout(r, 250));

    const entry = {
      viewport: vp.key,
      width: vp.w,
      issues: m.issues,
      icons: m.icons,
      gatewayCount: m.gatewayCount,
      brandCount: m.brandCount,
      hasContent: m.hasContent,
      shot,
    };
    results.viewports.push(entry);
    results.shots.push(shot);
    if (m.issues.length || !m.hasContent || !iconOk) results.pass = false;
  }

  // Dedicated full mobile + desktop named shots
  await page.setViewport({ width: 390, height: 900 });
  await page.goto(BASE, { waitUntil: "networkidle0" });
  results.shots.push(await fullPageShot(page, "vilag-mobile-full.png"));
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto(BASE, { waitUntil: "networkidle0" });
  results.shots.push(await fullPageShot(page, "vilag-desktop-full.png"));

  // Open places dialog on desktop
  await page.click('[data-open="places"]');
  await page.waitForSelector("dialog[open]");
  results.shots.push(
    await page.screenshot({
      path: path.join(SHOT_DIR, "vilag-desktop-places-dialog.png"),
      fullPage: false,
    }).then(() => path.join(SHOT_DIR, "vilag-desktop-places-dialog.png"))
  );
  await page.keyboard.press("Escape");
  await new Promise((r) => setTimeout(r, 200));

  // Planned shell click + bottom section crops
  await page.click("#esemenyek .event");
  await page.waitForSelector("dialog[open]", { timeout: 5000 }).catch(() => null);
  const plannedOk = await page.evaluate(() => {
    const d = document.querySelector("dialog");
    return !!(d && d.open && /Hamarosan itt is böngészhetsz/i.test(d.innerText));
  });
  if (!plannedOk) {
    results.pass = false;
    results.checks.push("planned_dialog_failed");
  }
  results.shots.push(
    await page.screenshot({
      path: path.join(SHOT_DIR, "vilag-desktop-planned-dialog.png"),
      fullPage: false,
    }).then(() => path.join(SHOT_DIR, "vilag-desktop-planned-dialog.png"))
  );

  await browser.close();

  const out = path.join(PROJECT, "TEST-RUN-VILAG.json");
  fs.writeFileSync(out, JSON.stringify(results, null, 2));
  const md = [
    "# ORBIT Világ ellenőrzés",
    "",
    `Result: **${results.pass ? "PASS" : "FAIL"}**`,
    "",
    "## Viewports",
    "",
    ...results.viewports.map(
      (v) =>
        `- ${v.viewport}px: gateways=${v.gatewayCount}, brands=${v.brandCount}, icons=${JSON.stringify(v.icons)}, issues=${v.issues.join("; ") || "none"} → \`${path.relative(PROJECT, v.shot)}\``
    ),
    "",
    "## Screenshots",
    "",
    ...results.shots.map((s) => `- \`${path.relative(PROJECT, s)}\``),
    "",
  ].join("\n");
  fs.writeFileSync(path.join(PROJECT, "TEST-RUN-VILAG.md"), md);
  console.log(JSON.stringify({ pass: results.pass, shots: results.shots.length, out }, null, 2));
  process.exit(results.pass ? 0 : 1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
