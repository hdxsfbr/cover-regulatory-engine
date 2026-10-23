import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

// All responses are local recorded/synthetic data; this can also test the running UI.
test("search, selection and refresh show immediate loading and recover", async ({
  page,
}) => {
  const context = JSON.parse(
    readFileSync(
      new URL("../../data/fixtures/2202010009.json", import.meta.url),
      "utf8",
    ),
  );
  Object.assign(context, {
    mode: "live",
    snapshot_id: "loading-test",
    applicability_fingerprint: "same",
  });
  let releaseSearch!: () => void;
  const searchGate = new Promise<void>((r) => (releaseSearch = r));
  let releaseContext!: () => void;
  const contextGate = new Promise<void>((r) => (releaseContext = r));
  let releaseRefresh!: () => void;
  const refreshGate = new Promise<void>((r) => (releaseRefresh = r));
  await page.route("**/*", (route) =>
    new URL(route.request().url()).hostname === "127.0.0.1"
      ? route.continue()
      : route.abort(),
  );
  await page.route("**/api/config", (route) =>
    route.fulfill({ json: { mode: "live", checks: {}, input_bounds: {} } }),
  );
  await page.route("**/api/parcels?query=*", async (route) => {
    await searchGate;
    await route.fulfill({
      json: { status: "matched", features: [{ properties: context.parcel }] },
    });
  });
  await page.route("**/api/parcels/2202010009/context*", async (route) => {
    if (route.request().url().includes("fresh=true")) {
      await refreshGate;
      await route.fulfill({
        status: 503,
        json: { detail: "Synthetic refresh outage" },
      });
    } else {
      await contextGate;
      await route.fulfill({ json: context });
    }
  });
  await page.route("**/api/assessments", (route) =>
    route.fulfill({
      json: {
        status: "partial",
        coverage: "Loading feedback test",
        constraints: [],
      },
    }),
  );
  await page.goto("/");
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
  const search = page.getByRole("button", { name: "Searching…" });
  await expect(search).toBeDisabled();
  await expect(search.locator(".spinner")).toBeVisible();
  await expect(page.getByRole("status")).toContainText(
    "Searching County parcel records",
  );
  releaseSearch();
  const candidate = page.locator(".candidate");
  await candidate.click();
  await expect(candidate).toHaveAttribute("aria-busy", "true");
  await expect(candidate).toBeDisabled();
  await expect(candidate).toContainText("Loading property");
  await expect(candidate.locator(".spinner")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Find property" }),
  ).toBeEnabled();
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(candidate.locator(".spinner")).toHaveCSS(
    "animation-name",
    "none",
  );
  await page.screenshot({ path: "test-results/loading.png", fullPage: true });
  releaseContext();
  await expect(page.locator(".property-title h2")).toContainText("7523");
  await expect(candidate).toHaveCount(0);
  await expect(page.locator(".spinner")).toHaveCount(0);
  await page.getByRole("button", { name: "Refresh parcel sources" }).click();
  const refresh = page.getByRole("button", { name: "Loading sources…" });
  await expect(refresh).toBeDisabled();
  await expect(refresh.locator(".spinner")).toBeVisible();
  releaseRefresh();
  await expect(page.getByRole("alert")).toContainText(
    "Synthetic refresh outage",
  );
  await expect(
    page.getByRole("button", { name: "Refresh parcel sources" }),
  ).toBeEnabled();
  await expect(page.locator(".spinner")).toHaveCount(0);
});
