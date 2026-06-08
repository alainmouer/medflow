import { test, expect } from "@playwright/test";

test("doctor can navigate to agenda page", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("link", { name: /Agenda/i }).click();
  await expect(page).toHaveURL(/\/agenda/);

  await expect(page.getByRole("heading", { name: /Agenda/i })).toBeVisible();

  // Vérifier les 2 onglets
  await expect(page.getByRole("button", { name: /Rendez-vous/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Missions terrain/i })).toBeVisible();

  // Le tableau doit être visible (même vide)
  await expect(page.getByRole("table")).toBeVisible();

  // Basculer sur l'onglet Missions terrain
  await page.getByRole("button", { name: /Missions terrain/i }).click();
  await expect(page.getByRole("table")).toBeVisible();
});
