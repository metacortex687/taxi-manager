import { expect, test } from '@playwright/test';

const EXTERNAL_TEST_URL = 'https://ya.ru/';

test('external HTTPS endpoint is reachable', async ({ request }) => {
  const response = await request.get(EXTERNAL_TEST_URL, {
    maxRedirects: 0,
    timeout: 30_000,
  });

  expect(response.status()).toBeGreaterThanOrEqual(200);
  expect(response.status()).toBeLessThan(400);
});