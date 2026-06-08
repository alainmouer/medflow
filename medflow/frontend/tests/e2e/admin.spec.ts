import { test, expect } from "@playwright/test";

test("admin can navigate to admin users page", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Admin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("link", { name: /Admin/i }).click();
  await expect(page).toHaveURL(/\/admin\/users/);

  await expect(page.getByRole("heading", { name: /Admin/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Créer/i })).toBeVisible();
});

test("doctor can navigate to ai prompts settings page", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.goto("/settings/ai-prompts");
  await expect(page).toHaveURL(/\/settings\/ai-prompts/);

  await expect(page.getByRole("heading", { name: /Paramètres IA/i })).toBeVisible();
});
