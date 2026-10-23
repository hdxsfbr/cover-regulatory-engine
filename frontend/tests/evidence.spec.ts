import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/*", (route) =>
    new URL(route.request().url()).hostname === "127.0.0.1"
      ? route.continue()
      : route.abort(),
  );
});

async function lookup(
  page: import("@playwright/test").Page,
  ain = "2202010009",
) {
  await page.goto("/");
  if (
    !(await page
      .getByLabel("Property address or assessor parcel number")
      .isVisible())
  )
    await page.locator("#property-search > summary").click();
  await page.getByLabel("Property address or assessor parcel number").fill(ain);
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator(".constraint")).toHaveCount(5);
}

test("map measurements eliminate transcription and blocker actions focus controls", async ({
  page,
}) => {
  await lookup(page);
  await expect(page.locator(".observation")).toHaveCount(3);
  await expect(
    page.locator(".constraint").first().locator(".blockers"),
  ).toContainText("Review the sourced legal lot depth");
  await page
    .locator(".constraint")
    .first()
    .getByRole("button", { name: "Review map evidence" })
    .click();
  await expect(page.locator("#parcel-evidence")).toBeFocused();
  for (const box of await page.locator(".observation input").all()) {
    await box.focus();
    await page.keyboard.press("Space");
  }
  await page
    .locator(".constraint")
    .nth(1)
    .getByRole("button", { name: "Enter proposed building height" })
    .click();
  await expect(page.locator("#input-building_height_ft")).toBeFocused();
  for (const key of ["lot_width_ft", "lot_depth_ft", "lot_area_sqft"]) {
    await expect(page.locator("#input-" + key)).toHaveValue("");
    await expect(page.locator("#input-" + key)).toBeDisabled();
  }
  await page.locator("#input-building_height_ft").fill("18");
  await page.locator("#input-roof_slope_percent").fill("20");
  for (const box of await page
    .locator(".input-panel input[type=checkbox]")
    .all())
    await box.check();
  await page
    .locator("#evidence-note")
    .fill(
      "Hypothetical project conditions for acceptance; sourced map readings accepted, not independent legal verification.",
    );
  await expect(page.locator(".badge.evaluated")).toHaveCount(5);
  await expect(page.locator(".value").nth(0)).toHaveText("20 ft");
  await expect(page.locator(".value").nth(4)).toHaveText("2,700 sq ft");
  await page.locator(".constraint").first().locator("summary").first().click();
  await expect(page.locator(".constraint").first()).toContainText(
    "document-accepted",
  );
  await page.screenshot({
    path: "test-results/evidence-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator(".observation").first()).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/evidence-mobile.png",
    fullPage: true,
  });
  await page.getByLabel("Project type").selectOption("adu");
  await expect(page.locator(".badge.conditional")).toHaveCount(4);
  await expect(
    page.locator(".constraint").first().locator(".blockers"),
  ).not.toContainText("Enter");
});

test("changed and failed refresh clear acceptance while retaining user work", async ({
  page,
}) => {
  await lookup(page);
  if (!(await page.locator(".observation input").first().isVisible()))
    await page
      .getByRole("button", { name: "Inspect evidence", exact: true })
      .click();
  await page.locator(".observation input").first().check();
  await page.locator(".input-panel summary").click();
  await page.locator("#input-building_height_ft").fill("19");
  await page.locator("#evidence-note").fill("Preserve my project basis");
  await page.route("**/api/parcels/*/context*", async (route) => {
    const r = await route.fetch();
    const d = await r.json();
    d.applicability_fingerprint = "changed-observation-version";
    await route.fulfill({ json: d });
  });
  await page
    .getByRole("button", { name: "Replay recorded evidence", exact: true })
    .first()
    .click();
  await expect(page.locator(".observation input").first()).not.toBeChecked();
  await expect(page.locator("#input-building_height_ft")).toHaveValue("19");
  await expect(page.locator("#evidence-note")).toHaveValue(
    "Preserve my project basis",
  );
  if (!(await page.locator(".observation input").first().isVisible()))
    await page
      .getByRole("button", { name: "Inspect evidence", exact: true })
      .click();
  await page.locator(".observation input").first().check();
  await page.route("**/api/parcels/*/context*", (route) =>
    route.fulfill({
      status: 503,
      json: { detail: "Synthetic document outage" },
    }),
  );
  await page
    .getByRole("button", { name: "Replay recorded evidence", exact: true })
    .first()
    .click();
  await expect(page.locator(".observation input").first()).not.toBeChecked();
  await expect(page.locator(".observation input").first()).toBeDisabled();
  await expect(page.locator(".constraint")).toHaveCount(0);
  await expect(page.locator("#evidence-note")).toHaveValue(
    "Preserve my project basis",
  );
});

test("late parcel response never restores old observation selection", async ({
  page,
}) => {
  await lookup(page);
  if (!(await page.locator(".observation input").first().isVisible()))
    await page
      .getByRole("button", { name: "Inspect evidence", exact: true })
      .click();
  await page.locator(".observation input").first().check();
  if (
    !(await page
      .getByLabel("Property address or assessor parcel number")
      .isVisible())
  )
    await page.locator("#property-search > summary").click();
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("LOUISE");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.route("**/api/parcels/2202010009/context*", async (route) => {
    const r = await route.fetch();
    await new Promise((r) => setTimeout(r, 800));
    await route.fulfill({ response: r });
  });
  await page.getByRole("button", { name: /7523 LOUISE/ }).click();
  await page.getByRole("button", { name: /7543 LOUISE/ }).click();
  await expect(page.locator(".property-title")).toContainText("7543");
  await page.waitForTimeout(1000);
  await expect(page.locator(".observation")).toHaveCount(0);
  await expect(
    page.locator(".constraint").first().locator(".blockers"),
  ).toBeVisible();
});
