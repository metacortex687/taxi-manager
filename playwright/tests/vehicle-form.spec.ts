import { test, expect } from '@playwright/test';

test('менеджер меняет бренд автомобиля', async ({ page }) => {
  const baseUrl = process.env.BASE_URL;

  if (!baseUrl) {
    throw new Error('Переменная BASE_URL не задана');
  }

  const url = baseUrl.replace(/\/$/, '');

  await page.goto(`${url}/login`);

  await page.getByRole('textbox', { name: 'Пользователь:' }).fill('manager1');
  await page.getByRole('textbox', { name: 'Пароль:' }).fill('manager1');
  await page.getByRole('button', { name: 'Войти' }).click();

  await page.getByRole('heading', { name: 'Hello world !!!' }).click();
  await page.goto(`${url}/`);

  await page.getByRole('link', { name: 'Предприятия' }).click();
  await page.getByRole('link', { name: 'Список' }).first().click();
  await page.getByRole('link', { name: 'Редактировать' }).first().click();

  const editUrl = page.url();

  await page.getByRole('textbox', { name: 'Приобретено:' }).fill('2026-07-15');
  await page.locator('#react-root').click();
  await page.getByLabel('Бренд:').selectOption('3');
  await page.getByRole('button', { name: 'Сохранить' }).click();

  await page.goto(editUrl);
  await page.locator('#react-root').click();

  await expect(page.getByLabel('Бренд:')).toHaveValue('3');
});