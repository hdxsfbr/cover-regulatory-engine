import { test, expect, type Page } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/*", (route) =>
    new URL(route.request().url()).hostname === "127.0.0.1"
      ? route.continue()
      : route.abort(),
  );
});

async function choose(page: Page, ain = "2202010009") {
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
async function enterFacts(page: Page) {
  await page
    .getByText("Project inputs & unresolved checks", {
      exact: true,
    })
    .click();
  await page.getByLabel("Legal lot width (ft)", { exact: true }).fill("40");
  for (const check of await page
    .locator(".input-panel")
    .getByRole("checkbox")
    .all())
    await check.check();
  await page
    .getByLabel("Evidence or basis for these inputs")
    .fill("Synthetic recovery test scenario");
}
const replay = (page: Page) =>
  page.getByRole("button", { name: "Replay recorded evidence" }).first();

test("recorded failure explains missing evidence and replay", async ({
  page,
}) => {
  await choose(page, "2202010006");
  await expect(
    page.getByText(/replay loads the same saved evidence/),
  ).toBeVisible();
  await expect(
    page
      .locator('[data-reason="source_unavailable"]')
      .filter({ hasText: "Chapter 1 zoning" }),
  ).toBeVisible();
  await expect(
    page.locator('[data-reason="zoning_multiple_matches"]'),
  ).toHaveCount(0);
  const source = page
    .locator('[data-reason="source_unavailable"] a')
    .filter({ hasText: "Chapter 1 zoning" });
  await expect(source).toHaveAttribute("href", /zimas.lacity.org/);
  await replay(page).click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await expect(
    page
      .locator('[data-reason="source_unavailable"]')
      .filter({ hasText: "Chapter 1 zoning" }),
  ).toBeVisible();
});

test("same evidence replay preserves inputs and conditional accessory packages", async ({
  page,
}) => {
  await choose(page);
  await enterFacts(page);
  await page.getByLabel("Project type").selectOption("adu");
  const response = page.waitForResponse(
    "**/api/parcels/2202010009/context?compact=true&fresh=true",
  );
  await replay(page).focus();
  await page.keyboard.press("Enter");
  await response;
  await expect(page.locator(".badge.conditional")).toHaveCount(4);
  await page.getByLabel("Project type").selectOption("single-family");
  await expect(
    page.getByLabel("Legal lot width (ft)", { exact: true }),
  ).toHaveValue("40");
  await expect(
    page.getByLabel("Evidence or basis for these inputs"),
  ).toHaveValue("Synthetic recovery test scenario");
  for (const check of await page
    .locator(".input-panel")
    .getByRole("checkbox")
    .all())
    await expect(check).toBeChecked();
  await page.getByLabel("Project type").selectOption("guest-house");
  await replay(page).click();
  await expect(page.locator(".badge.conditional")).toHaveCount(4);
});

test("changed evidence clears checks and uses replacement snapshot", async ({
  page,
}) => {
  await choose(page);
  await enterFacts(page);
  let replacement = "";
  await page.route("**/context?compact=true&fresh=true", async (route) => {
    const response = await route.fetch();
    const data = await response.json();
    data.applicability_fingerprint = "synthetic changed evidence";
    replacement = data.snapshot_id;
    await route.fulfill({ json: data });
  });
  const assessment = page.waitForRequest(
    (r) =>
      r.url().endsWith("/api/assessments") &&
      r.postDataJSON().snapshot_id === replacement,
  );
  await replay(page).click();
  await assessment;
  await expect(
    page.getByText(/Applicability evidence changed or could not be confirmed/),
  ).toBeVisible();
  for (const check of await page
    .locator(".input-panel")
    .getByRole("checkbox")
    .all())
    await expect(check).not.toBeChecked();
  await expect(
    page.getByLabel("Legal lot width (ft)", { exact: true }),
  ).toHaveValue("40");
  await expect(page.locator(".badge.needs-review")).toHaveCount(5);
});

test("transport failure keeps previous evidence without reevaluating it", async ({
  page,
}) => {
  await choose(page);
  await enterFacts(page);
  await page.route("**/context?compact=true&fresh=true", (route) =>
    route.fulfill({
      status: 503,
      json: { detail: "Synthetic context outage" },
    }),
  );
  await replay(page).click();
  await expect(
    page.getByText(/Previous evidence — assessment pending/),
  ).toBeVisible();
  await expect(page.getByRole("alert")).toHaveText("Synthetic context outage");
  await expect(page.locator(".constraint")).toHaveCount(0);
  await page.getByLabel("Legal lot width (ft)", { exact: true }).fill("41");
  await page.waitForTimeout(400);
  await expect(page.locator(".constraint")).toHaveCount(0);
  await page.unroute("**/context?compact=true&fresh=true");
  await replay(page).click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await expect(
    page.getByLabel("Legal lot width (ft)", { exact: true }),
  ).toHaveValue("41");
});

test("expired assessment can recover without losing dimensions", async ({
  page,
}) => {
  await choose(page);
  await enterFacts(page);
  let expire = true;
  await page.route("**/api/assessments", async (route) => {
    if (expire) {
      expire = false;
      await route.fulfill({
        status: 410,
        json: { detail: "Parcel context expired; reload it" },
      });
    } else await route.continue();
  });
  await page.getByLabel("Legal lot width (ft)", { exact: true }).fill("42");
  await expect(page.getByRole("alert")).toContainText("expired");
  await replay(page).click();
  await expect(page.locator(".constraint")).toHaveCount(5);
  await expect(
    page.getByLabel("Legal lot width (ft)", { exact: true }),
  ).toHaveValue("42");
});

test("live labeling and early parcel failure offer whole-context recovery", async ({
  page,
}) => {
  // Synthetic live-mode responses; no external GIS calls are made by this browser test.
  await page.route("**/api/config", async (route) => {
    const data = await (await route.fetch()).json();
    data.mode = "live";
    await route.fulfill({ json: data });
  });
  await page.route("**/api/parcels/2202010009/context*", async (route) => {
    const data = await (await route.fetch()).json();
    data.mode = "live";
    for (const r of Object.values(data.records) as any[]) r.origin = "live";
    if (!route.request().url().includes("fresh=true")) {
      delete data.parcel;
      data.map.features = [];
      data.applicability_fingerprint = null;
      data.records.Parcels.status = "unavailable";
      data.jurisdiction = "needs-review";
      data.zoning_status = "needs-review";
      data.diagnostics = [
        {
          code: "source_unavailable",
          message: "Synthetic parcel source unavailable",
          sources: ["Parcels"],
          retryable: true,
        },
      ];
    }
    await route.fulfill({ json: data });
  });
  await choose(page);
  await expect(page.getByText("LOS ANGELES · LIVE SOURCES")).toBeVisible();
  await expect(
    page.getByText("Synthetic parcel source unavailable", { exact: false }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Refresh parcel sources" })
    .first()
    .click();
  await expect(page.locator(".property-title h2")).toContainText("7523");
  await expect(page.locator(".constraint")).toHaveCount(5);
});

test("new parcel selection clears entries during pending refresh", async ({
  page,
}) => {
  await choose(page);
  await enterFacts(page);
  await page.route("**/context?compact=true&fresh=true", async (route) => {
    const response = await route.fetch();
    await new Promise((r) => setTimeout(r, 1000));
    await route.fulfill({ response }).catch(() => {});
  });
  await replay(page).click();
  if (
    !(await page
      .getByLabel("Property address or assessor parcel number")
      .isVisible())
  )
    await page.locator("#property-search > summary").click();
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010010");
  await page.getByRole("button", { name: /Find property|Searching/ }).click();
  await page.locator(".candidate").first().click();
  await expect(page.locator(".property-title h2")).toContainText("7517");
  await page.waitForTimeout(1200);
  await expect(page.locator(".property-title h2")).toContainText("7517");
  const panel = page.getByText("Project inputs & unresolved checks", {
    exact: true,
  });
  if (
    !(await page
      .getByLabel("Legal lot width (ft)", { exact: true })
      .isVisible())
  )
    await panel.click();
  await expect(
    page.getByLabel("Legal lot width (ft)", { exact: true }),
  ).toHaveValue("");
});

test("late assessment cannot overwrite a fresh result", async ({ page }) => {
  await choose(page);
  let delayed = false;
  await page.route("**/api/assessments", async (route) => {
    const request = route.request().postDataJSON();
    if (request.project_type === "adu") {
      delayed = true;
      const response = await route.fetch();
      await new Promise((r) => setTimeout(r, 1200));
      await route.fulfill({ response }).catch(() => {});
    } else await route.continue();
  });
  await page.getByLabel("Project type").selectOption("adu");
  await expect.poll(() => delayed).toBe(true);
  await page.getByLabel("Project type").selectOption("single-family");
  await replay(page).click();
  await expect(page.locator(".badge.needs-review")).toHaveCount(5);
  await page.waitForTimeout(1300);
  await expect(page.locator(".badge.needs-review")).toHaveCount(5);
});

for (const failure of [
  {
    name: "empty gateway error",
    status: 502,
    body: "",
    expected: "The API is unavailable (HTTP 502)",
  },
  {
    name: "HTML error",
    status: 503,
    body: "<html>upstream unavailable</html>",
    expected: "The API is unavailable (HTTP 503)",
  },
  {
    name: "empty successful response",
    status: 200,
    body: "",
    expected: "The server returned an unreadable response",
  },
]) {
  test(`handles ${failure.name} without a JSON parsing error`, async ({
    page,
  }) => {
    await choose(page);
    await page.route("**/context?compact=true&fresh=true", (route) =>
      route.fulfill({
        status: failure.status,
        contentType: "text/plain",
        body: failure.body,
      }),
    );
    await replay(page).click();
    await expect(page.getByRole("alert")).toContainText(failure.expected);
    await expect(page.getByRole("alert")).not.toContainText("JSON");
    await expect(replay(page)).toBeEnabled();
    await page.unroute("**/context?compact=true&fresh=true");
    await replay(page).click();
    await expect(page.locator(".constraint")).toHaveCount(5);
  });
}
