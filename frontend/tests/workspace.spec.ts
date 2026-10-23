import { test, expect } from "@playwright/test";
test("save, compare, reopen and submit revision-linked feedback", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await page.getByRole("button", { name: "Save / compare / ask" }).click();
  const unique = `Option ${Date.now()}`;
  await page.getByLabel("Scenario name").fill(unique + " A");
  await page
    .getByRole("button", { name: "Save scenario", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: unique + " A · selected" }),
  ).toBeVisible();
  await page.getByLabel("Project type").selectOption("adu");
  await page.locator(".input-panel summary").click();
  await page
    .getByLabel("An existing single-family dwelling is on this lot.")
    .selectOption("yes");
  await page
    .getByLabel(
      "This proposal is new detached construction, not an attached unit or conversion.",
    )
    .selectOption("yes");
  await page
    .getByLabel("The proposed unit includes kitchen facilities.")
    .selectOption("yes");
  await page
    .getByLabel("Applicable Coastal Act requirements have been resolved.")
    .selectOption("yes");
  await expect(page.locator(".badge.evaluated")).toHaveCount(4);
  await page.getByLabel("Scenario name").fill(unique + " B");
  await page
    .getByRole("button", { name: "Save scenario", exact: true })
    .click();
  await expect(page.locator(".scenario-comparison article")).toHaveCount(2);
  await page
    .getByLabel("Report a problem with this result")
    .fill("Review source currency for this test scenario.");
  await page.getByRole("button", { name: "Submit feedback" }).click();
  await expect(
    page.getByText("Feedback saved for operator review."),
  ).toBeVisible();
  const projectId = await page.getByLabel("Open saved project").inputValue();
  await page.reload();
  await page.getByRole("button", { name: "Open a saved project" }).click();
  await page.getByLabel("Open saved project").selectOption(projectId);
  await expect(page.locator(".scenario-comparison article")).toHaveCount(2);
  await page
    .getByRole("button", { name: unique + " B · selected", exact: true })
    .click();
  await expect(page.getByLabel("Project type")).toHaveValue("adu");
  await expect(page.locator(".badge.evaluated")).toHaveCount(4);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBeTruthy();
  await page.screenshot({
    path: "test-results/workspace-mobile.png",
    fullPage: true,
  });
});

test("operator sources require token and expose actual passages", async ({
  page,
}) => {
  await page.goto("/operator");
  await page.getByLabel("Operator token").fill("wrong");
  await page.getByRole("button", { name: "Unlock review workspace" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Operator token required",
  );
  await page.getByLabel("Operator token").fill("browser-test-operator");
  await page.getByRole("button", { name: "Unlock review workspace" }).click();
  await expect(
    page.getByRole("heading", { name: "Sources and passages" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Candidate correction and review" }),
  ).toBeVisible();
  await page.screenshot({
    path: "test-results/operator-desktop.png",
    fullPage: true,
  });
});
