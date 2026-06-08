import { test, expect } from "@playwright/test";

test("doctor can navigate to AI analysis page from patient", async ({ page }) => {
  // 1. Quick login as doctor
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  // 2. Go to patients list
  await page.goto("/patients");
  await expect(page.getByRole("heading", { name: /Patients/i })).toBeVisible();

  // 3. Click the first patient row (or link)
  const firstPatientLink = page.locator("a", { hasText: /Martin|Bernard/ }).first();
  await firstPatientLink.click();
  await expect(page).toHaveURL(/\/patients\//);

  // 4. Find the first "Analyser" button and click
  const analyzeBtn = page.getByRole("button", { name: /Analyser/i }).first();
  await expect(analyzeBtn).toBeVisible();
  await analyzeBtn.click();

  // 5. Verify navigated to analysis page
  await expect(page).toHaveURL(/\/episodes\/.+\/analyze/);
  await expect(page.getByRole("heading", { name: /Analyse IA/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Analyser l'épisode/i })).toBeVisible();
});

test("admin can login and reach patients list", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Admin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
  await page.goto("/patients");
  await expect(page.getByRole("heading", { name: /Patients/i })).toBeVisible();
});
