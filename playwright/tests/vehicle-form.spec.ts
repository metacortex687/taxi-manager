import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:8080/login');
  await page.getByRole('textbox', { name: 'Пользователь:' }).click();
  await page.getByRole('textbox', { name: 'Пользователь:' }).fill('manager1');
  await page.getByRole('textbox', { name: 'Пароль:' }).click();
  await page.getByRole('textbox', { name: 'Пароль:' }).fill('manager1');
  await page.getByRole('button', { name: 'Войти' }).click();
  await page.getByRole('heading', { name: 'Hello world !!!' }).click();
  await page.goto('http://localhost:8080/');
  await page.getByRole('link', { name: 'Предприятия' }).click();
  await page.getByRole('link', { name: 'Список' }).first().click();
  await page.getByRole('link', { name: 'Редактировать' }).first().click();
  await page.getByRole('textbox', { name: 'Приобретено:' }).fill('2026-07-15');
  await page.locator('#react-root').click();
  await page.getByLabel('Бренд:').selectOption('3');
  await page.getByRole('button', { name: 'Сохранить' }).click();
  await page.goto('http://localhost:8080/vehicles/2/edit/');
  await page.locator('#react-root').click();
  await expect(page.getByLabel('Бренд:')).toHaveValue('3');
});