import { test, expect } from "@playwright/test";

test("design conflicts, restoration, comparison and revision targeting form one usable workflow", async ({
  page,
}) => {
  await page.route("**/*", (r) =>
    new URL(r.request().url()).hostname === "127.0.0.1"
      ? r.continue()
      : r.abort(),
  );
  await page.goto("/");
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await expect(page.getByRole("button", { name: "Locate on map" })).toHaveCount(
    0,
  );
  await page.getByLabel("Project type").selectOption("adu");
  await page
    .getByRole("button", { name: "Edit project inputs", exact: true })
    .click();
  await page
    .getByLabel("Proposed building height (ft)", { exact: true })
    .fill("19");
  await expect(
    page.locator("#constraint-height .design-comparison"),
  ).toContainText("conditional");
  for (const label of [
    "An existing single-family dwelling is on this lot.",
    "This proposal is new detached construction, not an attached unit or conversion.",
    "The proposed unit includes kitchen facilities.",
    "Applicable Coastal Act requirements have been resolved.",
  ])
    await page.getByLabel(label, { exact: true }).selectOption("yes");
  const height = page.locator("#constraint-height .design-comparison");
  await expect(height).toContainText("Exceeds by 3 ft");
  await expect(height).toContainText("Proposed 19 ft · Limit 16 ft");
  await page
    .getByRole("button", { name: "Edit proposed height", exact: true })
    .click();
  await expect(
    page.getByLabel("Proposed building height (ft)", { exact: true }),
  ).toBeFocused();
  await page.getByRole("button", { name: "Save / compare / ask" }).click();
  const name = `Decision review ${Date.now()}`;
  await page.getByLabel("Scenario name").fill(name + " 19 ft");
  await page
    .getByRole("button", { name: "Save scenario", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Ask follow-up", exact: true }),
  ).toBeEnabled();
  const projectId = await page.getByLabel("Open saved project").inputValue();
  await page
    .getByLabel("Proposed building height (ft)", { exact: true })
    .fill("15");
  await expect(page.locator(".revision-status")).toContainText(
    "Unsaved changes",
  );
  await expect(
    page.getByRole("button", { name: "Ask follow-up", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Submit feedback", exact: true }),
  ).toBeDisabled();
  await page
    .getByRole("button", { name: "Restore saved design", exact: true })
    .click();
  await expect(
    page.getByLabel("Proposed building height (ft)", { exact: true }),
  ).toHaveValue("19");
  await expect(
    page.getByRole("button", { name: "Ask follow-up", exact: true }),
  ).toBeEnabled();
  await page
    .getByLabel("Proposed building height (ft)", { exact: true })
    .fill("16");
  await page.getByLabel("Scenario name").fill(name + " 16 ft");
  await page
    .getByRole("button", { name: "Save scenario", exact: true })
    .click();
  await expect(page.locator(".scenario-comparison article")).toHaveCount(2);
  await expect(
    page
      .locator(".scenario-comparison article")
      .filter({ hasText: name + " 19 ft" }),
  ).toContainText("Exceeds by 3 ft");
  await expect(
    page
      .locator(".scenario-comparison article")
      .filter({ hasText: name + " 16 ft" }),
  ).toContainText("within limit");
  await page.reload();
  await page
    .getByRole("button", { name: "Open a saved project", exact: true })
    .click();
  await page.getByLabel("Open saved project").selectOption(projectId);
  await expect(page.getByLabel("Project type")).toHaveValue("adu");
  await expect(page.locator(".revision-status")).toContainText(name + " 16 ft");
  await expect(
    page.getByRole("button", { name: "Ask follow-up", exact: true }),
  ).toBeEnabled();
  await page
    .getByRole("button", { name: "Edit project inputs", exact: true })
    .click();
  await expect(
    page.getByLabel("Proposed building height (ft)", { exact: true }),
  ).toHaveValue("16");
  await page
    .getByLabel("Evidence or basis for these inputs")
    .fill("Changed evidence basis");
  await expect(
    page.getByRole("button", { name: "Ask follow-up", exact: true }),
  ).toBeDisabled();
  await page
    .getByRole("button", { name: "Restore saved design", exact: true })
    .click();
  await page.getByLabel("Project type").selectOption("guest-house");
  await expect(page.locator(".revision-status")).toContainText(
    "Unsaved changes",
  );
  await page
    .getByRole("button", { name: "Restore saved design", exact: true })
    .click();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/design-decisions-mobile.png",
    fullPage: true,
  });
});

test("research guidance distinguishes sourced facts, unresolved work and contextual fields", async ({
  page,
}) => {
  await page.route("**/api/parcels/2202010009/context*", async (route) => {
    const data = await (await route.fetch()).json();
    data.sourced_facts = {
      outside_hillside_coastal: {
        state: "true",
        evidence: "Synthetic negative boundary screens",
        limitation: "Named layers only",
      },
    };
    await route.fulfill({ json: data });
  });
  await page.goto("/");
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await page
    .getByRole("button", { name: "Edit project inputs", exact: true })
    .click();
  await expect(
    page
      .locator(".research-guidance")
      .filter({ hasText: "Automatically established" }),
  ).toContainText("Named layers only");
  await expect(
    page.getByLabel(
      "Evidence establishes that the property is outside Hillside Areas and Coastal Zones.",
      { exact: true },
    ),
  ).toBeChecked();
  await page
    .getByLabel(
      "Evidence establishes that the property is outside Hillside Areas and Coastal Zones.",
      { exact: true },
    )
    .uncheck();
  await expect(
    page.locator(".research-guidance").filter({ hasText: "your override" }),
  ).toBeVisible();
  await expect(page.getByText(/Inspect the recorded lot layout/)).toBeVisible();
  await expect(
    page.getByText(/Context only — saved with this design/),
  ).toHaveCount(2);
});
