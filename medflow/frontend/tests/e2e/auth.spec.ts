import { test, expect } from "@playwright/test";

test("quick login as doctor works", async ({ page }) => {
  await page.goto("/login");
  
  // Click the Quick Login button for Doctor
  await page.getByRole("button", { name: /Médecin/i }).click();
  
  // Check if we are redirected to dashboard
  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole("heading", { name: /Tableau de bord/i })).toBeVisible();
});

test("quick login as admin works", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Admin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);
});
