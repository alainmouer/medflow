import { test, expect } from "@playwright/test";

test("doctor can navigate to billing page", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("link", { name: /Facturation/i }).click();
  await expect(page).toHaveURL(/\/billing/);

  await expect(page.getByRole("heading", { name: /Facturation/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Nouvelle facture/i })).toBeVisible();
});
