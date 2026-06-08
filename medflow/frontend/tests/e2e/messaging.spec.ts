import { test, expect } from "@playwright/test";

test("doctor can navigate to messages page", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.getByRole("link", { name: /Messages/i }).click();
  await expect(page).toHaveURL(/\/messages/);

  await expect(page.getByRole("heading", { name: /Messagerie/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Nouveau message/i })).toBeVisible();
});

test("command palette opens with Ctrl+K", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: /Médecin/i }).click();
  await expect(page).toHaveURL(/\/dashboard/);

  await page.keyboard.press("Control+k");
  await expect(page.getByRole("dialog", { name: /Command palette/i })).toBeVisible();
  await expect(page.getByPlaceholder(/Tapez une commande/i)).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog", { name: /Command palette/i })).not.toBeVisible();
});
