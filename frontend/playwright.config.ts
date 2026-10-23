import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  use: { baseURL: "http://127.0.0.1:5179" },
  webServer: [
    {
      command:
        "COVER_DATABASE=/tmp/cover-playwright-workspace.sqlite3 COVER_OPERATOR_TOKEN=browser-test-operator COVER_FIXTURE_MODE=1 uv run --project .. uvicorn backend.app:app --app-dir .. --port 18081",
      url: "http://127.0.0.1:18081/api/config",
      reuseExistingServer: false,
    },
    {
      command:
        "COVER_API_URL=http://127.0.0.1:18081 npm run dev -- --port 5179 --strictPort",
      url: "http://127.0.0.1:5179",
      reuseExistingServer: false,
    },
  ],
});
