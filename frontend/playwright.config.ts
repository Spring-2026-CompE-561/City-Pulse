import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/integration",
  timeout: 60_000,
  use: {
    baseURL: "http://127.0.0.1:3000",
  },
  webServer: [
    {
      command: "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
      cwd: "..",
      url: "http://127.0.0.1:8000/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        PYTHONPATH: "src",
        DATABASE_URL: "mysql+asyncmy://test:test@127.0.0.1:3306/city_pulse?charset=utf8mb4",
        JWT_SECRET_KEY: "integration-test-secret-key-0123456789",
        CORS_ALLOW_ORIGINS: "http://127.0.0.1:3000",
        SKIP_DB_INIT: "true",
      },
    },
    {
      command: "npm run dev -- --port 3000",
      url: "http://127.0.0.1:3000/",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:8000",
      },
    },
  ],
});
