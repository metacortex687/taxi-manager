import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

import { chromium } from "playwright-core";

const diagramsUrl = process.argv[2];
const outputDirectory = process.argv[3] ?? "/output";
const timeoutMs = Number.parseInt(
  process.env.STRUCTURIZR_EXPORT_TIMEOUT_MS ?? "120000",
  10,
);

if (!diagramsUrl) {
  console.error(
    "Usage: export-png.mjs <Structurizr diagrams URL> [output directory]",
  );
  process.exit(2);
}

if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
  console.error("STRUCTURIZR_EXPORT_TIMEOUT_MS must be a positive integer");
  process.exit(2);
}

const delay = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

async function openStructurizr(page) {
  const deadline = Date.now() + timeoutMs;
  let lastError;

  while (Date.now() < deadline) {
    try {
      const response = await page.goto(diagramsUrl, {
        waitUntil: "domcontentloaded",
        timeout: 10000,
      });

      if (response === null || response.ok()) {
        return;
      }

      lastError = new Error(
        `Structurizr returned HTTP ${response.status()} ${response.statusText()}`,
      );
    } catch (error) {
      lastError = error;
    }

    await delay(1000);
  }

  throw new Error(
    `Structurizr did not become available within ${timeoutMs} ms`,
    { cause: lastError },
  );
}

function pngBufferFromDataUri(dataUri) {
  const prefix = "data:image/png;base64,";

  if (typeof dataUri !== "string" || !dataUri.startsWith(prefix)) {
    throw new Error("Structurizr returned an invalid PNG data URI");
  }

  return Buffer.from(dataUri.slice(prefix.length), "base64");
}

await fs.mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  args: ["--no-sandbox"],
});

try {
  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 },
  });

  console.log(`Opening ${diagramsUrl}`);
  await openStructurizr(page);

  await page.waitForFunction(
    () =>
      window.structurizr?.scripting !== undefined &&
      window.structurizr.scripting.isDiagramRendered() === true,
    undefined,
    { timeout: timeoutMs },
  );

  const views = await page.evaluate(() =>
    window.structurizr.scripting.getViews().map((view) => ({
      key: view.key,
      type: view.type,
    })),
  );

  if (views.length === 0) {
    throw new Error("The Structurizr workspace does not contain any views");
  }

  for (const view of views) {
    if (!/^[A-Za-z0-9._-]+$/.test(view.key)) {
      throw new Error(`View key cannot be used as a filename: ${view.key}`);
    }

    await page.evaluate(
      (viewKey) => window.structurizr.scripting.changeView(viewKey),
      view.key,
    );

    await page.waitForFunction(
      (viewKey) =>
        window.structurizr.scripting.getViewKey() === viewKey &&
        window.structurizr.scripting.isDiagramRendered() === true,
      view.key,
      { timeout: timeoutMs },
    );

    const dataUri = await page.evaluate(
      (exportTimeoutMs) =>
        new Promise((resolve, reject) => {
          const timer = window.setTimeout(
            () => reject(new Error("PNG export callback timed out")),
            exportTimeoutMs,
          );

          window.structurizr.scripting.exportCurrentDiagramToPNG(
            { includeMetadata: true, crop: false },
            (png) => {
              window.clearTimeout(timer);
              resolve(png);
            },
          );
        }),
      timeoutMs,
    );

    const outputPath = path.join(outputDirectory, `${view.key}.png`);
    await fs.writeFile(outputPath, pngBufferFromDataUri(dataUri));
    console.log(`Saved ${outputPath}`);
  }

  console.log(`Exported ${views.length} diagrams`);
} finally {
  await browser.close();
}
