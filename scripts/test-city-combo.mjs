/**
 * Regression: searchable city combobox in Üzletek és szervizek filter.
 */
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT = path.resolve(__dirname, "..");
const BASE = process.env.BASE_URL || "http://127.0.0.1:8772/";
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const OUT = path.join(PROJECT, "TEST-CITY-COMBO.json");

async function openPlaces(page) {
  await page.goto(BASE, { waitUntil: "networkidle0", timeout: 60000 });
  // Gateway / nav entry for places
  const clicked = await page.evaluate(() => {
    const byData = document.querySelector('[data-open="places"]');
    if (byData) {
      byData.click();
      return "data-open";
    }
    const link = [...document.querySelectorAll("a,button")].find((el) =>
      /üzletek|szerviz/i.test(el.textContent || "")
    );
    if (link) {
      link.click();
      return "text";
    }
    return null;
  });
  if (!clicked) throw new Error("places entry not found");
  await page.waitForSelector("#place-filter [data-city-combo]", { timeout: 8000 });
}

async function runViewport(browser, w, h) {
  const page = await browser.newPage();
  await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
  await openPlaces(page);

  const cases = [];

  // Open combo, type accentless partial
  await page.click("#city-combo-trigger");
  await page.waitForSelector("#city-combo-panel:not([hidden])");
  await page.type("#city-combo-search", "szekes", { delay: 15 });
  await page.waitForFunction(() => {
    const opts = [...document.querySelectorAll("#city-listbox [role=option]")];
    return opts.some((o) => /székesfehérvár/i.test(o.textContent || ""));
  });
  const afterType = await page.evaluate(() => {
    const opts = [...document.querySelectorAll("#city-listbox [role=option]")].map(
      (o) => o.textContent
    );
    return {
      opts,
      emptyHidden: document.getElementById("city-combo-empty").hidden,
      searchVisible: !!(
        document.getElementById("city-combo-search") &&
        getComputedStyle(document.getElementById("city-combo-search")).display !==
          "none"
      ),
    };
  });
  cases.push({
    id: "type-szekes-finds-szekesfehervar",
    pass:
      afterType.searchVisible &&
      afterType.opts.some((o) => /székesfehérvár/i.test(o)) &&
      afterType.emptyHidden,
    detail: afterType,
  });

  // Select city via click
  await page.evaluate(() => {
    const opt = [...document.querySelectorAll("#city-listbox [role=option]")].find(
      (o) => /székesfehérvár/i.test(o.textContent || "")
    );
    opt.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
  });
  await page.waitForFunction(
    () =>
      document.getElementById("place-city-value")?.value === "Székesfehérvár" &&
      document.getElementById("city-combo-panel")?.hidden
  );
  const selected = await page.evaluate(() => ({
    value: document.getElementById("place-city-value").value,
    trigger: document.getElementById("city-combo-trigger").textContent.trim(),
    countText: document.querySelector(".meta-line")?.textContent || "",
    listCities: [...document.querySelectorAll(".place-list li")].map((li) =>
      li.textContent
    ),
  }));
  cases.push({
    id: "select-updates-list",
    pass:
      selected.value === "Székesfehérvár" &&
      selected.trigger === "Székesfehérvár" &&
      selected.listCities.length > 0 &&
      selected.listCities.every((t) => /székesfehérvár/i.test(t)),
    detail: selected,
  });

  // Clear via Minden település
  await page.click("#city-combo-trigger");
  await page.waitForSelector("#city-combo-panel:not([hidden])");
  await page.evaluate(() => {
    const opt = [...document.querySelectorAll("#city-listbox [role=option]")].find(
      (o) => o.textContent.trim() === "Minden település"
    );
    opt.dispatchEvent(new MouseEvent("mousedown", { bubbles: true }));
  });
  await page.waitForFunction(
    () => document.getElementById("place-city-value")?.value === ""
  );
  const cleared = await page.evaluate(() => ({
    value: document.getElementById("place-city-value").value,
    trigger: document.getElementById("city-combo-trigger").textContent.trim(),
  }));
  cases.push({
    id: "clear-all-cities",
    pass: cleared.value === "" && /minden település/i.test(cleared.trigger),
    detail: cleared,
  });

  // No match
  await page.click("#city-combo-trigger");
  await page.type("#city-combo-search", "xyzzyqwerty", { delay: 10 });
  const miss = await page.evaluate(() => ({
    emptyHidden: document.getElementById("city-combo-empty").hidden,
    emptyText: document.getElementById("city-combo-empty").textContent,
    hasAll: [...document.querySelectorAll("#city-listbox [role=option]")].some(
      (o) => o.textContent.trim() === "Minden település"
    ),
  }));
  cases.push({
    id: "no-match-message",
    pass:
      !miss.emptyHidden &&
      /nincs ilyen település/i.test(miss.emptyText) &&
      miss.hasAll,
    detail: miss,
  });

  // Escape closes without changing filter (set city first)
  await page.evaluate(() => {
    document.getElementById("city-combo-search").value = "";
    document.getElementById("city-combo-search").dispatchEvent(new Event("input"));
  });
  await page.keyboard.press("Escape");
  await page.waitForFunction(() => document.getElementById("city-combo-panel")?.hidden);
  const afterEsc = await page.evaluate(() => ({
    value: document.getElementById("place-city-value").value,
    open: !document.getElementById("city-combo-panel").hidden,
  }));
  cases.push({
    id: "escape-keeps-filter",
    pass: afterEsc.value === "" && !afterEsc.open,
    detail: afterEsc,
  });

  // Keyboard: open, type debrec, Enter selects first ranked city
  await page.click("#city-combo-trigger");
  await page.waitForSelector("#city-combo-panel:not([hidden])");
  await page.$eval("#city-combo-search", (el) => {
    el.value = "";
  });
  await page.type("#city-combo-search", "debrec", { delay: 12 });
  await page.keyboard.press("ArrowDown"); // move to first city after ALL
  await page.keyboard.press("Enter");
  await page.waitForFunction(
    () => document.getElementById("place-city-value")?.value === "Debrecen"
  );
  const kb = await page.evaluate(() => document.getElementById("place-city-value").value);
  cases.push({
    id: "keyboard-select-debrecen",
    pass: kb === "Debrecen",
    detail: { value: kb },
  });

  await page.close();
  return { viewport: `${w}x${h}`, pass: cases.every((c) => c.pass), cases };
}

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu"],
  });
  const report = { accessedAt: new Date().toISOString(), base: BASE, pass: true, viewports: [] };
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
  console.log(
    JSON.stringify(
      {
        pass: report.pass,
        out: OUT,
        viewports: report.viewports.map((v) => ({
          viewport: v.viewport,
          pass: v.pass,
          fails: v.cases.filter((c) => !c.pass).map((c) => c.id),
        })),
      },
      null,
      2
    )
  );
  if (!report.pass) process.exit(1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
