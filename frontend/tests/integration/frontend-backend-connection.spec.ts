import { expect, test } from "@playwright/test";

test("frontend proxy reaches backend health endpoint", async ({ request }) => {
  const response = await request.get("/api/health");
  expect(response.status()).toBe(200);

  const payload = await response.json();
  expect(payload).toEqual({
    status: "ok",
    service: "City Pulse API",
  });
});
