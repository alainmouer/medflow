import { test, expect } from "@playwright/test";

test("doctor can navigate to AI analysis page from patient", async ({ page }) => {
  // 1. Quick login as doctor
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  // 2. Go to patients list
  await page.goto("/patients");
  await expect(page.getByRole("heading", { name: /Patients/i })).toBeVisible();

  // 3. Wait for patients table to load and click first row text (Martin)
  await page.waitForSelector('table tbody tr', { timeout: 10000 });
  await page.getByRole("cell", { name: /Martin/i }).first().click();
  await expect(page).toHaveURL(/\/patients\//);

  // 4. Find the first "Analyser" button and click
  const analyzeBtn = page.getByRole("button", { name: /Analyser/i }).first();
  await expect(analyzeBtn).toBeVisible();
  await analyzeBtn.click();

  // Wait for analysis page navigation
  await page.waitForURL(/\/episodes\/.+\/analyze/, { timeout: 10000 });
  await page.waitForLoadState("domcontentloaded");

  // 5. Verify navigated to analysis page
  await expect(page.getByRole("heading", { name: /Analyse IA/i })).toBeVisible({ timeout: 10000 });
});

test("admin can login and reach patients list", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Admin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await page.goto("/patients");
  await expect(page.getByRole("heading", { name: /Patients/i })).toBeVisible();
});
