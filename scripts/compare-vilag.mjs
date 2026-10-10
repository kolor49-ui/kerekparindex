/**
 * Side-by-side ORBIT Világ: reference HTML vs integrated local site.
 */
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import http from "node:http";
import { execSync } from "node:child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT = path.resolve(__dirname, "..");
const REF = path.join(PROJECT, "reference", "kerekparindex-orbit-vilag.html");
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const OUT = path.join(PROJECT, "screenshots", "orbit-vilag-compare");
const LIVE = process.env.BASE_URL || "http://127.0.0.1:8767/";

const VIEWPORTS = [
  { w: 390, h: 900, key: "mobile" },
  { w: 1440, h: 900, key: "desktop" },
];

function startStatic(root, port) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let urlPath = decodeURIComponent((req.url || "/").split("?")[0]);
      if (urlPath === "/") urlPath = "/index.html";
      const file = path.join(root, urlPath.replace(/^\//, ""));
      fs.readFile(file, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end("missing");
          return;
        }
        const ext = path.extname(file);
        const types = {
          ".html": "text/html",
          ".css": "text/css",
          ".js": "text/javascript",
          ".json": "application/json",
          ".png": "image/png",
        };
        res.writeHead(200, { "Content-Type": types[ext] || "text/plain" });
        res.end(data);
      });
    });
    server.listen(port, "127.0.0.1", () => resolve(server));
  });
}

async function measure(page) {
  return page.evaluate(() => {
    const brands = [...document.querySelectorAll(".brands .brand")].map((b) =>
      b.textContent.trim()
    );
    const chips = [...document.querySelectorAll(".search-tabs .chip")]
      .filter((c) => getComputedStyle(c).display !== "none")
      .map((c) => c.textContent.trim());
    const gateways = [...document.querySelectorAll(".gateways .gateway")]
      .filter((g) => getComputedStyle(g).display !== "none")
      .map((g) => g.querySelector("strong")?.textContent.trim());
    const nav = [...document.querySelectorAll(".nav a")]
      .filter((a) => getComputedStyle(a).display !== "none")
      .map((a) => a.textContent.trim());
    const intro = document.querySelector(".intro p")?.innerText.replace(/\s+/g, " ").trim();
    const demo = !!document.querySelector(".demo");
    const icons = [...document.querySelectorAll(".gateways .gateway .icon")]
      .filter((el) => {
        const g = el.closest(".gateway");
        return g && getComputedStyle(g).display !== "none";
      })
      .map((el) => {
        const r = el.getBoundingClientRect();
        return { w: Math.round(r.width), h: Math.round(r.height) };
      });
    return { brands, chips, gateways, nav, intro, demo, icons, nGateways: gateways.length };
  });
}

async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  // Serve reference as standalone file via temp dir
  const refDir = fs.mkdtempSync(path.join("/tmp", "kpi-ref-"));
  fs.copyFileSync(REF, path.join(refDir, "index.html"));
  const refServer = await startStatic(refDir, 8768);
  const siteServer = await startStatic(PROJECT, 8767);

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: "new",
    args: ["--no-sandbox", "--disable-gpu"],
  });
  const report = { pass: true, viewports: [], shots: [] };

  for (const vp of VIEWPORTS) {
    const page = await browser.newPage();
    await page.setViewport({ width: vp.w, height: vp.h, deviceScaleFactor: 1 });

    await page.goto("http://127.0.0.1:8768/", { waitUntil: "networkidle0" });
    // Hide demo bar for visual parity with live (demo removed on purpose)
    await page.evaluate(() => {
      const d = document.querySelector(".demo");
      if (d) d.style.display = "none";
    });
    const refM = await measure(page);
    const refShot = path.join(OUT, `ref-${vp.key}.png`);
    await page.screenshot({ path: refShot, fullPage: true });

    await page.goto(LIVE, { waitUntil: "networkidle0" });
    const liveM = await measure(page);
    const liveShot = path.join(OUT, `live-${vp.key}.png`);
    await page.screenshot({ path: liveShot, fullPage: true });

    const issues = [];
    if (liveM.nGateways !== 6) issues.push("gateways:" + liveM.nGateways);
    if (liveM.chips.length !== 5) issues.push("chips:" + liveM.chips.length);
    if (liveM.brands.join("|") !== "CUBE|TREK|GIANT|GEPIDA|SPECIALIZED|MERIDA")
      issues.push("brands:" + liveM.brands.join("|"));
    if (liveM.demo) issues.push("demo_present");
    if (!/Márkák, bringák, jó helyek/.test(liveM.intro || ""))
      issues.push("intro_mismatch");
    if (liveM.nav.length < 7) issues.push("nav_count:" + liveM.nav.length);

    // desktop icon sizes ~23
    if (vp.w >= 651) {
      const bad = liveM.icons.filter((i) => i.w < 20 || i.w > 28);
      if (bad.length) issues.push("icon_size");
    }

    const entry = {
      viewport: vp.key,
      width: vp.w,
      issues,
      ref: refM,
      live: liveM,
      refShot,
      liveShot,
    };
    report.viewports.push(entry);
    report.shots.push(refShot, liveShot);
    if (issues.length) report.pass = false;
    await page.close();
  }

  await browser.close();
  refServer.close();
  siteServer.close();

  const md = [
    "# ORBIT Világ — referencia vs. integrált",
    "",
    `Result: **${report.pass ? "PASS" : "FAIL"}**`,
    "",
    "A referencia demósávját a képen elrejtettük (az élesen szándékosan nincs).",
    "",
    ...report.viewports.flatMap((v) => [
      `## ${v.viewport} (${v.width}px)`,
      "",
      `- Referencia: \`${path.relative(PROJECT, v.refShot)}\``,
      `- Integrált: \`${path.relative(PROJECT, v.liveShot)}\``,
      `- Kapuk: ${v.live.nGateways} · Chipek: ${v.live.chips.length} · Márkák: ${v.live.brands.join(", ")}`,
      `- Issues: ${v.issues.join("; ") || "none"}`,
      "",
    ]),
  ].join("\n");
  fs.writeFileSync(path.join(PROJECT, "TEST-RUN-VILAG-COMPARE.md"), md);
  fs.writeFileSync(
    path.join(PROJECT, "TEST-RUN-VILAG-COMPARE.json"),
    JSON.stringify(report, null, 2)
  );
  console.log(JSON.stringify({ pass: report.pass, out: OUT }, null, 2));
  process.exit(report.pass ? 0 : 1);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
