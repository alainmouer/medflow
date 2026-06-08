import { test, expect } from "@playwright/test";

test("homepage has title and login link", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/MedFlow/);
  await expect(page.getByRole("link", { name: /Connexion/i })).toBeVisible();
});
