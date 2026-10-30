import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.E2E_BASE_URL || "http://127.0.0.1:5173",
    channel: "chrome",
    trace: "retain-on-failure",
  },
  webServer: process.env.E2E_BASE_URL ? undefined : [
    {
      command:
        process.platform === "win32"
          ? "..\\.venv\\Scripts\\python -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 8000"
          : "../.venv/bin/python -m uvicorn app.main:app --app-dir ../backend --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: true,
    },
    {
      command: "npm run dev",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: true,
    },
  ],
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    {
      name: "mobile",
      use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" },
    },
  ],
});
