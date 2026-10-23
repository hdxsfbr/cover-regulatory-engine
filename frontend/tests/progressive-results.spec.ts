import { test, expect } from "@playwright/test";

for (const outcome of ["measurements", "empty", "failed"]) {
  test(`progressive findings remain useful through ${outcome}`, async ({
    page,
  }) => {
    let context: any;
    let stage = "finding-tract-map";
    let finished = false;
    await page.route("**/*", (r) =>
      new URL(r.request().url()).hostname === "127.0.0.1"
        ? r.continue()
        : r.abort(),
    );
    await page.route("**/api/parcels/2202010009/context*", async (route) => {
      context = await (await route.fetch()).json();
      context.mode = "live";
      context.document.status = "available";
      delete context.automatic_evidence;
      await route.fulfill({ json: context });
    });
    await page.route("**/api/evidence-jobs", (route) =>
      route.fulfill({
        json: { id: "progress-test", status: "running", stage },
      }),
    );
    await page.route("**/api/evidence-jobs/progress-test", (route) =>
      route.fulfill({
        json: {
          id: "progress-test",
          status: finished
            ? outcome === "failed"
              ? "failed"
              : "completed"
            : "running",
          stage,
          error:
            finished && outcome === "failed"
              ? "Synthetic reader failure"
              : undefined,
        },
      }),
    );
    await page.route("**/api/evidence-jobs/progress-test/context", (route) =>
      route.fulfill({
        json: {
          ...context,
          automatic_evidence: {
            observations:
              outcome === "measurements"
                ? [
                    {
                      key: "lot_depth_ft",
                      value: 120,
                      units: "ft",
                      reason: "Synthetic validated depth",
                      confidence_reason: "Synthetic test evidence",
                      page: 1,
                      document_hash: "a".repeat(64),
                      source_url: "https://example.test/map.pdf",
                      region: [0, 0, 0.5, 0.5],
                    },
                  ]
                : [],
            uncertainties: ["Applicability still needs review"],
          },
        },
      }),
    );
    await page.goto("/");
    await page
      .getByLabel("Property address or assessor parcel number")
      .fill("2202010009");
    await page.getByRole("button", { name: "Find property" }).click();
    await page.locator(".candidate").first().click();
    const progress = page.getByRole("region", { name: "Assessment progress" });
    await expect(progress).toContainText("Start with these findings");
    await expect(progress).toContainText("R1-1");
    await expect(progress).toContainText("of 5 have values");
    await expect(
      page.getByText(/Finding the recorded tract map/),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "View available results", exact: true })
      .click();
    await expect(page.locator("#assessment-results")).toBeFocused();
    await page
      .getByRole("button", {
        name: "Enter design while maps load",
        exact: true,
      })
      .click();
    await page
      .getByLabel("Proposed building height (ft)", { exact: true })
      .fill("19");
    await expect(page.locator(".constraint")).toHaveCount(5);
    stage = "reading-map";
    await expect(
      page.getByText(/Reading lot boundaries and dimensions/),
    ).toBeVisible();
    await page.getByRole("button", { name: "Results", exact: true }).click();
    await page.setViewportSize({ width: 390, height: 844 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
    if (outcome === "measurements") {
      await progress.scrollIntoViewIfNeeded();
      await page.screenshot({
        path: "test-results/progressive-loading-mobile.png",
      });
    }
    finished = true;
    if (outcome === "failed") {
      await expect(page.getByRole("alert")).toContainText(
        "Available parcel facts and preliminary results are still usable",
      );
      await expect(
        page.getByRole("button", { name: "Retry automatic map reading" }),
      ).toBeVisible();
    } else {
      await expect(progress).toContainText("Map reading finished");
      await expect(page.locator(".reading-complete")).toContainText(
        outcome === "empty"
          ? "No usable dimensions were established"
          : "120 ft",
      );
    }
    await expect(
      page.getByLabel("Proposed building height (ft)", { exact: true }),
    ).toHaveValue("19");
    await expect(page.locator(".constraint")).toHaveCount(5);
  });
}
