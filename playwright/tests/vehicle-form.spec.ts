import { test, expect } from '@playwright/test';

test('менеджер меняет бренд автомобиля', async ({ page }) => {
  const baseUrl = process.env.BASE_URL;

  await page.goto(`${baseUrl}/login`);

  await page.getByLabel('Пользователь:').fill('manager1');
  await page.getByLabel('Пароль:').fill('manager1');
  await page.getByRole('button', { name: 'Войти' }).click();

  await page.getByRole('link', { name: 'Предприятия' }).click();
  await page.getByRole('link', { name: 'Список' }).first().click();
  await page.getByRole('link', { name: 'Редактировать' }).first().click();

  const editUrl = page.url();
  const brand = page.getByLabel('Бренд:');

  await page.getByLabel('Приобретено:').fill('2026-07-15');
  await brand.selectOption('3');
  await page.getByRole('button', { name: 'Сохранить' }).click();

  await page.goto(editUrl);

  await expect(page.getByLabel('Бренд:')).toHaveValue('3');
});