import { test, expect, type Page } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/*", (r) =>
    new URL(r.request().url()).hostname === "127.0.0.1"
      ? r.continue()
      : r.abort(),
  );
});
async function choose(page: Page) {
  await page.goto("/");
  await page
    .getByLabel("Property address or assessor parcel number")
    .fill("2202010009");
  await page.getByRole("button", { name: "Find property" }).click();
  await expect(
    page.getByRole("heading", { name: "Choose a property" }),
  ).toBeVisible();
  const candidate = page.getByRole("button", {
    name: /7523 LOUISE.*Open assessment/,
  });
  await candidate.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator(".constraint")).toHaveCount(5);
}

test("decision order, targeted focus and drafts survive secondary disclosures", async ({
  page,
}) => {
  await choose(page);
  await expect(page.locator(".candidate")).toHaveCount(0);
  await expect(page.locator(".intro")).toHaveCount(0);
  const order = await page.evaluate(() =>
    [
      "property-overview",
      "assessment-results",
      "input-panel",
      "parcel-evidence",
      "project-tools",
    ].map((id) => {
      const el = document.getElementById(id)!;
      return [...document.querySelectorAll("*")].indexOf(el);
    }),
  );
  expect(order).toEqual([...order].sort((a, b) => a - b));
  await expect(page.locator("#parcel-evidence")).not.toHaveAttribute("open");
  await expect(page.locator("#project-tools")).not.toHaveAttribute("open");
  await page
    .getByRole("button", { name: "Review next item", exact: true })
    .focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#parcel-evidence")).toBeFocused();
  await expect(page.locator(".observation").first()).toBeVisible();
  await page
    .getByRole("button", { name: "Edit project inputs", exact: true })
    .click();
  await expect(page.locator("#input-panel")).toBeFocused();
  await page
    .getByLabel("Proposed building height (ft)", { exact: true })
    .fill("19");
  await page.getByRole("button", { name: "Save / compare / ask" }).click();
  await page.getByLabel("Scenario name").fill("Unsubmitted design draft");
  await page.locator("#project-tools > summary").click();
  await page.getByRole("button", { name: "Save / compare / ask" }).click();
  await expect(page.getByLabel("Scenario name")).toHaveValue(
    "Unsubmitted design draft",
  );
  await expect(
    page.getByLabel("Proposed building height (ft)", { exact: true }),
  ).toHaveValue("19");
  await page.locator("#project-tools > summary").click();
  await page.locator("#input-panel > summary").click();
  await page.locator("#parcel-evidence > summary").click();
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.screenshot({
    path: "test-results/reorganized-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  for (const type of ["single-family", "adu", "guest-house"]) {
    await page.getByLabel("Project type").selectOption(type);
    await expect(page.locator(".constraint")).toHaveCount(
      type === "single-family" ? 5 : 4,
    );
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
  }
  await page.screenshot({
    path: "test-results/reorganized-mobile.png",
    fullPage: true,
  });
  await page.locator("#property-search > summary").focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByLabel("Property address or assessor parcel number"),
  ).toBeVisible();
});

test("background map reading can cancel and retry while evidence stays collapsed", async ({
  page,
}) => {
  await page.route("**/api/parcels/2202010009/context*", async (route) => {
    const data = await (await route.fetch()).json();
    data.mode = "live";
    data.document.status = "available";
    delete data.automatic_evidence;
    await route.fulfill({ json: data });
  });
  let cancelled = false;
  let starts = 0;
  await page.route("**/api/evidence-jobs", (route) => {
    starts++;
    cancelled = false;
    return route.fulfill({
      json: { id: "layout-job", status: "running", stage: "reading-map" },
    });
  });
  await page.route("**/api/evidence-jobs/layout-job", (route) =>
    route.fulfill({
      json: {
        id: "layout-job",
        status: cancelled ? "cancelled" : "running",
        stage: "reading-map",
      },
    }),
  );
  await page.route("**/api/evidence-jobs/layout-job/cancel", (route) => {
    cancelled = true;
    return route.fulfill({
      json: { id: "layout-job", status: "cancelled", stage: "cancelled" },
    });
  });
  await choose(page);
  await expect(page.locator("#parcel-evidence")).not.toHaveAttribute("open");
  await expect(page.getByText(/Reading public map:/)).toBeVisible();
  const initialStarts = starts;
  await page.getByRole("button", { name: "Cancel map reading" }).click();
  await page
    .getByRole("button", { name: "Retry automatic map reading" })
    .click();
  await expect.poll(() => starts).toBe(initialStarts + 1);
  await expect(
    page.getByRole("button", { name: "Cancel map reading" }),
  ).toBeVisible();
});

test("completed machine readings, source crops and uncertainties stay reachable", async ({
  page,
}) => {
  await page.route("**/api/parcels/2202010009/context*", async (route) => {
    const data = await (await route.fetch()).json();
    data.automatic_evidence = {
      observations: [
        {
          key: "lot_depth_ft",
          value: 120,
          units: "ft",
          reason: "Synthetic printed-depth reading",
          method: "derived-midpoint-depth",
          assumptions: ["Synthetic opposite rear-boundary assumption"],
          operands: [
            {
              role: "side_a",
              length_ft: 110,
              bearing: "N00°00'00\"E",
              page: 3,
              source_url: "https://example.test/tract.pdf",
              document_hash: "b".repeat(64),
            },
          ],
          citations: [
            {
              url: "https://example.test/definition",
              section: "Synthetic lot-depth definition",
              source_hash: "c".repeat(64),
            },
          ],
          page: 1,
          source_url: "https://example.test/map.pdf",
          confidence_reason: "Synthetic corroboration",
          document_hash: "a".repeat(64),
          region: [0.1, 0.1, 0.3, 0.3],
        },
      ],
      uncertainties: ["Synthetic frontage uncertainty retained"],
    };
    await route.fulfill({ json: data });
  });
  await choose(page);
  await expect(page.getByText(/Public map reading complete/)).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Automatic map readings" }),
  ).not.toBeVisible();
  await page.getByRole("button", { name: "Inspect map readings" }).click();
  await expect(
    page.getByRole("heading", { name: "Automatic map readings" }),
  ).toBeVisible();
  await expect(
    page.getByText("Synthetic frontage uncertainty retained"),
  ).toBeVisible();
  await expect(
    page.getByText("Lot depth · derived", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Synthetic opposite rear-boundary assumption"),
  ).toBeVisible();
  await page.getByText("How this depth was derived", { exact: true }).click();
  await expect(
    page.getByRole("link", { name: "Synthetic lot-depth definition" }),
  ).toHaveAttribute("href", "https://example.test/definition");
  await page.getByText("Inspect printed measurement", { exact: true }).click();
  await expect(
    page.getByRole("img", { name: "Source crop for lot_depth_ft" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Open full source page" }),
  ).toHaveAttribute("href", /\/pages\/1$/);
});

test("map and constraint links and conditional export survive compact results", async ({
  page,
}) => {
  await page.route("**/api/assessments", async (route) => {
    const data = await (await route.fetch()).json();
    data.constraints[0].blockers = [
      {
        code: "missing_inputs",
        message: "Missing or unresolved: lot_depth_ft, frontage_reviewed",
        target: "input-panel",
        action: "input",
        label: "Review project facts",
      },
    ];
    data.geometry = {
      type: "FeatureCollection",
      metadata: {
        status: "conditional",
        scope: "Synthetic UI linkage example",
        calculation_crs: "EPSG:2229",
      },
      features: [
        {
          type: "Feature",
          properties: { category: "front-yard", setback_ft: 20 },
          geometry: {
            type: "LineString",
            coordinates: [
              [-118.509, 34.207],
              [-118.5088, 34.207],
            ],
          },
        },
      ],
    };
    await route.fulfill({ json: data });
  });
  await choose(page);
  const row = page.locator("#constraint-front-yard");
  await expect(row.locator(".blockers")).toContainText(
    "Legal lot depth (ft), frontage and neighboring setbacks",
  );
  await expect(row.locator(".blockers")).not.toContainText("lot_depth_ft");
  await row.getByRole("button", { name: "Locate on map" }).click();
  const highlighted = page.locator('.map path[stroke="#a44524"]');
  await expect(highlighted).toHaveCount(1);
  await highlighted.dispatchEvent("click");
  await expect(row).toBeFocused();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export setback GeoJSON" }).click();
  const file = await download;
  const stream = await file.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
  expect(JSON.parse(Buffer.concat(chunks).toString()).metadata.status).toBe(
    "conditional",
  );
  await expect(page.getByText(/conditional setback envelope/)).toBeVisible();
});
