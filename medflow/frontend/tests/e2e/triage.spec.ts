import { test, expect } from "@playwright/test";

test("doctor can navigate to triage page", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await expect(page.getByRole("heading", { name: /Tableau de bord/i })).toBeVisible();

  await page.getByRole("link", { name: /Triage/i }).click();
  await expect(page).toHaveURL(/\/triage/);

  await expect(page.getByRole("heading", { name: /Triage/i })).toBeVisible();

  // Attendre que le tableau apparaisse (même vide)
  await expect(page.getByRole("table")).toBeVisible();
});
