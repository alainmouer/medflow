import { test, expect } from "@playwright/test";

test("homepage has title and login link", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/MedFlow/);
  await expect(page.getByRole("link", { name: /Connexion/i })).toBeVisible();
});

test("login page renders form", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: /MedFlow/i })).toBeVisible();
  await expect(page.getByPlaceholder(/doctor@medflow.fr/i)).toBeVisible();
  await expect(page.getByRole("button", { name: /Se connecter/i })).toBeVisible();
});
