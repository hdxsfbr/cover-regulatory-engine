import { test, expect } from "@playwright/test";

test("independent research, retry, saved provenance and mobile layout", async ({
  page,
}) => {
  let fail = true;
  await page.route("**/api/research/permits", async (route) => {
    if (fail)
      await route.fulfill({
        status: 503,
        json: { detail: "Permit source temporarily unavailable" },
      });
    else await route.continue();
  });
  await page.goto("/");
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await page
    .getByRole("button", { name: "Property research", exact: true })
    .click();
  await expect(page.locator("#parcel-research")).toBeFocused();
  const permits = page.getByLabel("Permit history", { exact: true });
  await expect(permits).toContainText("Lookup failed");
  await permits.locator("summary").first().click();
  await expect(permits).toContainText("temporarily unavailable");
  const planning = page.getByLabel("Planning profile & cases", { exact: true });
  await expect(planning).toContainText("Not checked");
  fail = false;
  await permits.getByRole("button", { name: "Retry permit history" }).click();
  await expect(permits).toContainText("Recorded mode");
  await expect(page.locator("#parcel-research")).toContainText(
    "4/4 sources returned",
  );
  await page.getByRole("button", { name: "Save / compare / ask" }).click();
  const name = `Research ${Date.now()}`;
  await page.getByLabel("Scenario name").fill(name);
  await page
    .getByRole("button", { name: "Save scenario", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: name + " · selected", exact: true }),
  ).toBeVisible();
  const project = await page.getByLabel("Open saved project").inputValue();
  await page.reload();
  await page.getByRole("button", { name: "Open a saved project" }).click();
  await page.getByLabel("Open saved project").selectOption(project);
  await expect(page.locator("#parcel-research")).toContainText(
    "4/4 sources returned",
  );
  await page
    .getByRole("button", { name: "Property research", exact: true })
    .click();
  await permits.locator("summary").first().click();
  await permits.getByRole("button", { name: "Refresh permit history" }).click();
  await expect(page.locator(".project-workspace")).toContainText(
    "Unsaved changes",
  );
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
});

test("late research cannot populate a newly selected parcel", async ({
  page,
}) => {
  let delayed = false;
  await page.route("**/api/research/permits", async (route) => {
    const response = await route.fetch();
    const data = await response.json();
    if (!delayed) {
      delayed = true;
      await new Promise((r) => setTimeout(r, 2500));
      data.summary = "OLD PARCEL RECORD";
    }
    await route.fulfill({ json: data }).catch(() => {});
  });
  await page.goto("/");
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await page.getByText("Change property", { exact: true }).click();
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010006");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator("#parcel-research")).toContainText(
    "4/4 sources returned",
  );
  await page.waitForTimeout(2700);
  await expect(page.locator("#parcel-research")).not.toContainText(
    "OLD PARCEL RECORD",
  );
});
