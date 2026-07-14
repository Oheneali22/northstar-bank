import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const dashboardUrl = new URL("../app/BankDashboard.tsx", import.meta.url);
const pageUrl = new URL("../app/page.tsx", import.meta.url);
const layoutUrl = new URL("../app/layout.tsx", import.meta.url);

test("dashboard exposes the initial customer workflows", async () => {
  const [dashboard, page, layout] = await Promise.all([
    readFile(dashboardUrl, "utf8"),
    readFile(pageUrl, "utf8"),
    readFile(layoutUrl, "utf8"),
  ]);

  assert.match(layout, /Northstar Bank/);
  assert.match(page, /BankDashboard/);
  assert.match(dashboard, /Available balance/);
  assert.match(dashboard, /Recent transactions/);
  assert.match(dashboard, /All systems operational/);
  assert.match(dashboard, /submitTransfer/);
  assert.doesNotMatch(dashboard, /codex-preview|react-loading-skeleton/i);
});
