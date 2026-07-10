import http from 'k6/http';
import { check, fail } from 'k6';

export const MODEL_PREFIX = 'perf_test_model_';
export const MODEL_IDS_READ_LIMIT = 10;

export const BASE_URL = requiredEnv('TARGET_BASE_URL').replace(/\/+$/, '');

export const MODEL_SYNC_URL = `${BASE_URL}/api/v1/models/`;
export const MODEL_ASYNC_URL = `${BASE_URL}/api/v1/rust/models/batch-queue/`;
//export const MODEL_ASYNC_URL = `${BASE_URL}/api/v1/rust/models/`;

export const MODEL_URL = MODEL_ASYNC_URL;
export const AUTH_TOKEN = requiredEnv('AUTH_TOKEN');

export const SUMMARY_TREND_STATS = [
  'avg',
  'min',
  'med',
  'p(90)',
  'p(95)',
  'p(99)',
  'max',
];

export function authHeaders() {
  return {
    Authorization: `Token ${AUTH_TOKEN}`,
  };
}

export function jsonHeaders() {
  return {
    ...authHeaders(),
    'Content-Type': 'application/json',
  };
}

export function modelBody(name) {
  return {
    name,
    type: 'PCR',
    number_of_seats: 5,
    tank_capacity_l: 20,
    load_capacity_kg: 500,
  };
}

export function scenario(operationType, rate, durationSeconds, startTimeSeconds, experiment, preAllocatedVUs, maxVUs) {
  return {
    executor: 'constant-arrival-rate',
    rate,
    timeUnit: '1s',
    duration: `${durationSeconds}s`,
    startTime: `${startTimeSeconds}s`,
    preAllocatedVUs,
    maxVUs,
    gracefulStop: '0s',
    tags: {
      experiment,
      endpoint: 'models',
      phase: 'measure',
      operation_type: operationType,
      target_rps: String(rate),
    },
  };
}

export function measureTags(experiment, operationType, targetRps, operation, name) {
  return {
    name,
    experiment,
    endpoint: 'models',
    phase: 'measure',
    operation_type: operationType,
    target_rps: String(targetRps),
    operation,
  };
}

export function setupTags(experiment, operation, name) {
  return {
    name,
    experiment,
    endpoint: 'models',
    phase: 'setup',
    operation_type: 'setup',
    operation,
  };
}

export function deleteTestData(experiment) {
  console.log(`!!!! Путь: ${MODEL_SYNC_URL}delete-test-data/`);
  const response = http.del(
    `${MODEL_SYNC_URL}delete-test-data/`,
    null,
    {
      headers: authHeaders(),
      tags: setupTags(experiment, 'delete_test_data', 'DELETE /api/v1/models/delete-test-data/'),
    },
  );

  console.log(
    `DEBUG delete-test-data: ` +
    `url=${MODEL_SYNC_URL}delete-test-data/, ` +
    `status=${response.status}, ` +
    `body=${String(response.body).slice(0, 500)}`,
  );

  const ok = check(response, {
    'delete test data status is 200': (r) => r.status === 200,
  });

  if (!ok) {
    fail(
      `Не удалось очистить тестовые данные. ` +
      `status=${response.status}, ` +
      `body=${String(response.body).slice(0, 500)}`,
    );
  }

  console.log(`Очистка тестовых данных: ${response.body}`);
}

export function loadModelIdsByHeavyList(experiment) {
  const ids = [];
  let url = MODEL_SYNC_URL;
  let page = 0;

  while (url) {
    page += 1;

    const response = http.get(
      url,
      {
        headers: authHeaders(),
        tags: setupTags(experiment, 'load_model_ids_heavy', 'GET /api/v1/models/'),
      },
    );

    const ok = check(response, {
      'heavy load ids status is 200': (r) => r.status === 200,
    });

    if (!ok) {
      fail(
        `Не удалось загрузить ids тяжёлым списком. ` +
        `page=${page}, ` +
        `status=${response.status}, ` +
        `url=${url}, ` +
        `body=${String(response.body).slice(0, 500)}`,
      );
    }

    const contentType = response.headers['Content-Type'] || '';

    if (!contentType.includes('application/json')) {
      fail(
        `Ожидался JSON при загрузке ids тяжёлым списком. ` +
        `page=${page}, ` +
        `status=${response.status}, ` +
        `contentType=${contentType}, ` +
        `url=${url}, ` +
        `body=${String(response.body).slice(0, 500)}`,
      );
    }

    const data = response.json();
    const results = Array.isArray(data) ? data : data.results || [];

    for (const model of results) {
      if (String(model.name).startsWith(MODEL_PREFIX)) {
        ids.push(model.id);

        if (ids.length >= MODEL_IDS_READ_LIMIT) {
          break;
        }
      }
    }

    console.log(`Прочитана страница моделей: page=${page}, найдено ids=${ids.length}`);

    if (ids.length >= MODEL_IDS_READ_LIMIT) {
      console.log(`Достигнут лимит чтения ids: limit=${MODEL_IDS_READ_LIMIT}`);
      break;
    }

    url = Array.isArray(data) ? null : data.next || null;
  }

  if (ids.length === 0) {
    fail(`GET /api/v1/models/ не нашёл записей с prefix=${MODEL_PREFIX}`);
  }

  return ids;
}

export function logIds(label, ids) {
  if (ids.length === 0) {
    console.log(`${label}: count=0`);
    return;
  }

  let minId = ids[0];
  let maxId = ids[0];

  for (const id of ids) {
    if (id < minId) {
      minId = id;
    }

    if (id > maxId) {
      maxId = id;
    }
  }

  console.log(`${label}: count=${ids.length}, min_id=${minId}, max_id=${maxId}`);
}

export function totalIterations(rates, durationSeconds) {
  return rates.reduce((sum, rate) => sum + rate * durationSeconds, 0);
}

function requiredEnv(name) {
  const value = __ENV[name];

  if (value === undefined || String(value).trim() === '') {
    throw new Error(`Required environment variable ${name} is not set`);
  }

  return String(value).trim();
}