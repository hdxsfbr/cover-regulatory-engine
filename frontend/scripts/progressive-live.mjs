import { chromium, expect } from "@playwright/test";
import fs from "node:fs/promises";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 1000 } });
const dir = new URL("../../data/delivery/progressive-results", import.meta.url)
  .pathname;
const start = Date.now();
const errors = [];
p.on("pageerror", (e) => errors.push(String(e)));
try {
  await p.goto("http://127.0.0.1:5173");
  await p
    .getByLabel("Property address or assessor parcel number")
    .fill("17413 Lemac St Los Angeles");
  await p.getByRole("button", { name: "Find property" }).click();
  await p.locator(".candidate").first().click();
  const progress = p.getByRole("region", { name: "Assessment progress" });
  await expect(progress).toBeVisible({ timeout: 35000 });
  await p.locator(".constraint").first().waitFor();
  const initialMs = Date.now() - start;
  const editedWhileReading = await p
    .getByRole("button", { name: "Enter design while maps load", exact: true })
    .isVisible();
  await p
    .getByRole("button", {
      name: editedWhileReading
        ? "Enter design while maps load"
        : "Edit design inputs",
      exact: true,
    })
    .click();
  await p
    .getByLabel("Proposed building height (ft)", { exact: true })
    .fill("19");
  await p
    .getByRole("button", { name: "View available results", exact: true })
    .click();
  await expect(p.locator("#assessment-results")).toBeFocused();
  await progress.scrollIntoViewIfNeeded();
  await p.screenshot({ path: dir + "/while-reading.png" });
  console.log("Early results usable", initialMs);
  await p
    .getByRole("button", { name: "Inspect map readings", exact: true })
    .waitFor({ timeout: 245000 });
  await expect(progress).toContainText("Map reading finished");
  await expect(
    p.getByLabel("Proposed building height (ft)", { exact: true }),
  ).toHaveValue("19");
  await expect(p.locator(".constraint")).toHaveCount(5);
  await progress.scrollIntoViewIfNeeded();
  await p.screenshot({ path: dir + "/completed.png" });
  await p.setViewportSize({ width: 390, height: 844 });
  expect(
    await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
  ).toBeTruthy();
  await p.screenshot({ path: dir + "/mobile.png" });
  await fs.writeFile(
    dir + "/live-proof.json",
    JSON.stringify(
      {
        query: "17413 Lemac St Los Angeles",
        initialMs,
        completeMs: Date.now() - start,
        editedWhileReading,
        heightPreserved: "19",
        reading: await p.locator(".reading-complete").innerText(),
        errors,
      },
      null,
      2,
    ),
  );
  expect(errors).toEqual([]);
  console.log("Live progressive workflow passed");
} finally {
  await b.close();
}
