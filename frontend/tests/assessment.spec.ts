import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/*", (route) =>
    new URL(route.request().url()).hostname === "127.0.0.1"
      ? route.continue()
      : route.abort(),
  );
});

test("recorded lookup, keyboard evidence, five calculations and conditional accessory packages", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByText("Recorded demonstration data", { exact: false }),
  ).toBeVisible();
  if (
    !(await page
      .getByLabel("Property address or assessor parcel number")
      .isVisible())
  )
    await page.locator("#property-search > summary").click();
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202-010-009");
  await page.getByRole("button", { name: "Find property" }).click();
  const candidate = page.getByRole("button", { name: /7523 LOUISE/ });
  await candidate.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".constraint")).toHaveCount(5);
  await expect(
    page.getByRole("img", {
      name: "Selected parcel boundary and mapped building footprints",
    }),
  ).toBeVisible();
  const evidence = page
    .locator("summary")
    .filter({ hasText: "Evidence & explanation" })
    .first();
  await evidence.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".citation a").first()).toBeVisible();
  await page
    .getByText("Project inputs & unresolved checks", {
      exact: true,
    })
    .click();
  for (const [label, value] of [
    ["Legal lot depth (ft)", "80"],
    ["Legal lot width (ft)", "40"],
    ["Legal lot area (sq ft)", "6000"],
    ["Proposed building height (ft)", "18"],
    ["Uppermost roof slope (%)", "20"],
  ])
    await page.getByLabel(label, { exact: true }).fill(value);
  for (const checkbox of await page
    .locator(".input-panel")
    .getByRole("checkbox")
    .all())
    await checkbox.check();
  await page
    .getByLabel("Evidence or basis for these inputs")
    .fill(
      "Hypothetical browser acceptance scenario, not actual site measurements.",
    );
  await expect(page.locator(".badge.evaluated")).toHaveCount(5);
  await expect(page.locator(".value").nth(0)).toHaveText("16 ft");
  await expect(page.locator(".value").nth(1)).toHaveText("4 ft");
  await expect(page.locator(".value").nth(4)).toHaveText("2,700 sq ft");
  await page
    .getByLabel("Proposed building height (ft)", { exact: true })
    .fill("28.1");
  await expect(page.locator(".value").nth(1)).toHaveText("6 ft");
  await page.getByLabel("Project type").selectOption("adu");
  await expect(page.locator(".badge.conditional")).toHaveCount(4);
  await page.getByLabel("Project type").selectOption("guest-house");
  await expect(page.locator(".badge.conditional")).toHaveCount(4);
  await page.screenshot({
    path: "test-results/assessment.png",
    fullPage: true,
  });
});

test("ambiguous address and stale parcel response", async ({ page }) => {
  await page.goto("/");
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
  await expect(page.locator(".candidate")).toHaveCount(4);
  await page.route(
    "**/api/parcels/2202010009/context?compact=true",
    async (route) => {
      const response = await route.fetch();
      await new Promise((resolve) => setTimeout(resolve, 1200));
      await route.fulfill({ response });
    },
  );
  await page.getByRole("button", { name: /7523 LOUISE/ }).click();
  await page.getByRole("button", { name: /7517 LOUISE/ }).click();
  await expect(page.locator(".property-title h2")).toContainText("7517");
  await page.waitForTimeout(1500);
  await expect(page.locator(".property-title h2")).toContainText("7517");
});

test("Rhea ambiguity, Chapter 1A, and source failure stay explicit", async ({
  page,
}) => {
  await page.goto("/");
  for (const [apn, expected] of [
    ["2126037055", "needs-review"],
    ["5138014112", "unsupported"],
  ]) {
    if (
      !(await page
        .getByLabel("Property address or assessor parcel number")
        .isVisible())
    )
      await page.locator("#property-search > summary").click();
    await page
      .getByLabel("Property address or assessor parcel number")
      .fill(apn);
    await page.getByRole("button", { name: "Find property" }).click();
    await page.locator(".candidate").first().click();
    await expect(page.locator(`.badge.${expected}`)).toHaveCount(5);
  }
  await page.route(
    "**/api/parcels/2202010009/context?compact=true",
    async (route) => {
      const response = await route.fetch();
      const data = await response.json();
      data.records.Buildings = {
        ...data.records.Buildings,
        status: "unavailable",
        error: "Synthetic upstream timeout",
      };
      data.map.features = data.map.features.filter(
        (f: any) => f.properties.kind === "parcel",
      );
      await route.fulfill({ json: data });
    },
  );
  if (
    !(await page
      .getByLabel("Property address or assessor parcel number")
      .isVisible())
  )
    await page.locator("#property-search > summary").click();
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(
    page.getByRole("img", {
      name: "Selected parcel boundary and mapped building footprints",
    }),
  ).toBeVisible();
  await page
    .getByText("Sources checked & data freshness", { exact: true })
    .click();
  await expect(page.getByText(/Synthetic upstream timeout/)).toBeVisible();
});
