import http from 'k6/http';
import { check, fail } from 'k6';
import exec from 'k6/execution';

// ========================
// Настройки теста
// ========================

const WRITE_RATES = [50, 100, 150, 180, 200, 240, 280, 350];
const READ_RATES = [50, 100, 120, 150, 180, 200, 240];
const DELETE_RATES = [10, 20, 50, 80, 100];
// const WRITE_RATES = [10, 20,];
// const READ_RATES = [10, 20,];
// const DELETE_RATES = [10, 20,];

const WRITE_DURATION_SECONDS = 61;
const READ_DURATION_SECONDS = 61;
const DELETE_DURATION_SECONDS = 61;

const WAIT_BEFORE_READ_SECONDS = 60;
const WAIT_BEFORE_DELETE_SECONDS = 60;

const PRE_ALLOCATED_VUS = 50;
const MAX_VUS = 200;

const EXPERIMENT = 'models_write_read_delete_ladder';
const ENDPOINT = 'models';

const MODEL_PATH = '/api/v1/models/';
const MODEL_NAME_PREFIX = 'perf_test_model_';

const BASE_URL = requiredEnv('TARGET_BASE_URL');
const AUTH_TOKEN = requiredEnv('AUTH_TOKEN');

const MODEL_URL = `${BASE_URL}${MODEL_PATH}`;

const MODEL_LIST_NAME = 'GET /api/v1/models/';
const MODEL_CREATE_NAME = 'POST /api/v1/models/';
const MODEL_DETAIL_READ_NAME = 'GET /api/v1/models/:id/';
const MODEL_DETAIL_DELETE_NAME = 'DELETE /api/v1/models/:id/';

const MODEL_DELETE_TEST_DATA_URL = `${MODEL_URL}delete-test-data/`;

let readModelIds = null;
let deleteModelIds = null;

// ========================
// Сценарии k6
// ========================

const scenarios = {};
const scenarioMeta = {};

let startTimeSeconds = 0;
let writeOffset = 0;

for (const rate of WRITE_RATES) {
  const name = `write_${rate}_rps`;
  const capacity = rate * WRITE_DURATION_SECONDS;

  scenarioMeta[name] = {
    operationType: 'write',
    rate,
    offset: writeOffset,
    limit: capacity,
  };

  scenarios[name] = scenario('write', rate, WRITE_DURATION_SECONDS, startTimeSeconds);

  startTimeSeconds += WRITE_DURATION_SECONDS;
  writeOffset += capacity;
}

startTimeSeconds += WAIT_BEFORE_READ_SECONDS;

for (const rate of READ_RATES) {
  const name = `read_${rate}_rps`;

  scenarioMeta[name] = {
    operationType: 'read',
    rate,
  };

  scenarios[name] = scenario('read', rate, READ_DURATION_SECONDS, startTimeSeconds);

  startTimeSeconds += READ_DURATION_SECONDS;
}

startTimeSeconds += WAIT_BEFORE_DELETE_SECONDS;

let deleteOffset = 0;

for (const rate of DELETE_RATES) {
  const name = `delete_${rate}_rps`;
  const capacity = rate * DELETE_DURATION_SECONDS;

  scenarioMeta[name] = {
    operationType: 'delete',
    rate,
    offset: deleteOffset,
    limit: capacity,
  };

  scenarios[name] = scenario('delete', rate, DELETE_DURATION_SECONDS, startTimeSeconds);

  startTimeSeconds += DELETE_DURATION_SECONDS;
  deleteOffset += capacity;
}

export const options = {
  setupTimeout: '20m',
  teardownTimeout: '5m',
  scenarios,

  summaryTrendStats: [
    'avg',
    'min',
    'med',
    'p(50)',
    'p(90)',
    'p(95)',
    'p(99)',
    'max',
  ],

  thresholds: {
    http_req_failed: ['rate<0.05'],
  },
};

// ========================
// Проверка перед стартом
// ========================

export function setup() {
  const response = http.del(
    MODEL_DELETE_TEST_DATA_URL,
    null,
    {
      headers: authHeaders(),
    },
  );

  const cleanupOk = check(response, {
    'delete test data status is 200': (r) => r.status === 200,
  });

  if (!cleanupOk) {
    fail(`Не удалось очистить тестовые данные ${MODEL_NAME_PREFIX}. Status: ${response.status}. Body: ${response.body}`);
  }

  console.log(`Очистка тестовых данных ${MODEL_NAME_PREFIX}: ${response.body}`);
}

// ========================
// Основная функция
// ========================

export default function () {
  const meta = scenarioMeta[exec.scenario.name];

  if (meta.operationType === 'write') {
    createModel(meta);
    return;
  }

  if (meta.operationType === 'read') {
    readModel(meta);
    return;
  }

  if (meta.operationType === 'delete') {
    deleteModel(meta);
    return;
  }
}

// ========================
// Операции
// ========================

function createModel(meta) {
  const iteration = exec.scenario.iterationInTest;

  if (iteration >= meta.limit) {
    return;
  }

  const modelNumber = meta.offset + iteration + 1;
  const name = `${MODEL_NAME_PREFIX}${modelNumber}`;

  const response = http.post(
    MODEL_URL,
    JSON.stringify({
      name,
      type: 'PCR',
      number_of_seats: 5,
      tank_capacity_l: 20,
      load_capacity_kg: 500,
    }),
    {
      headers: jsonHeaders(),
      tags: measureTags(meta, 'create_model', MODEL_CREATE_NAME),
    },
  );

  check(response, {
    'create status is 201': (r) => r.status === 201,
  });
}

function readModel(meta) {
  if (readModelIds === null) {
    readModelIds = shuffleIds(loadPerfModelIds('read'));
  }

  if (readModelIds.length === 0) {
    fail(`Не найдены записи ${MODEL_NAME_PREFIX} для чтения.`);
  }

  const index = exec.scenario.iterationInTest % readModelIds.length;
  const modelId = readModelIds[index];

  const response = http.get(
    `${MODEL_URL}${modelId}/`,
    {
      headers: authHeaders(),
      tags: measureTags(meta, 'read_model', MODEL_DETAIL_READ_NAME),
    },
  );

  check(response, {
    'read status is 200': (r) => r.status === 200,
  });
}

function deleteModel(meta) {
  if (deleteModelIds === null) {
    deleteModelIds = shuffleIds(loadPerfModelIds('delete'));
  }

  const iteration = meta.offset + exec.scenario.iterationInTest;

  if (iteration >= deleteModelIds.length) {
    return;
  }

  const modelId = deleteModelIds[iteration];

  const response = http.del(
    `${MODEL_URL}delete-test-data/`,
    null,
    {
      headers: authHeaders(),
      tags: measureTags(meta, 'delete_model', MODEL_DETAIL_DELETE_NAME),
    },
  );

  check(response, {
    'delete status is 204': (r) => r.status === 204,
  });
}

function deleteModels(ids) {
  for (let index = 0; index < ids.length; index += 1) {
    const modelId = ids[index];

    const response = http.del(
      `${MODEL_URL}${modelId}/`,
      null,
      {
        headers: authHeaders(),
        tags: setupTags('delete_old_model', MODEL_DETAIL_DELETE_NAME),
      },
    );

    check(response, {
      'delete old model status is 204': (r) => r.status === 204,
    });

    if ((index + 1) % 500 === 0) {
      console.log(`Удалено старых записей: ${index + 1}/${ids.length}`);
    }
  }
}

// ========================
// Получение созданных id
// ========================

function loadPerfModelIds(operationType) {
  const ids = [];
  let url = MODEL_URL;

  while (url) {
    const response = http.get(url, {
      headers: authHeaders(),
      tags: operationType === 'setup'
        ? setupTags('load_model_ids', MODEL_LIST_NAME)
        : supportTags(operationType, 'load_model_ids', MODEL_LIST_NAME),
    });

    const ok = check(response, {
      'load ids status is 200': (r) => r.status === 200,
    });

    if (!ok) {
      fail(
        `Не удалось загрузить id моделей. ` +
        `operationType=${operationType}, ` +
        `status=${response.status}, ` +
        `url=${url}, ` +
        `body=${String(response.body).slice(0, 500)}`
      );
    }

    const contentType = response.headers['Content-Type'] || '';

    if (!contentType.includes('application/json')) {
      fail(
        `Ожидался JSON при загрузке id моделей, но пришел другой ответ. ` +
        `operationType=${operationType}, ` +
        `status=${response.status}, ` +
        `contentType=${contentType}, ` +
        `url=${url}, ` +
        `body=${String(response.body).slice(0, 500)}`
      );
    }

    const data = response.json();
    const results = Array.isArray(data) ? data : data.results || [];

    for (const model of results) {
      if (String(model.name).startsWith(MODEL_NAME_PREFIX)) {
        ids.push(model.id);
      }
    }

    url = data.next || null;
  }

  return ids;
}

// ========================
// Вспомогательные функции
// ========================

function scenario(operationType, rate, durationSeconds, startTimeSeconds) {
  return {
    executor: 'constant-arrival-rate',
    rate,
    timeUnit: '1s',
    duration: `${durationSeconds}s`,
    preAllocatedVUs: PRE_ALLOCATED_VUS,
    maxVUs: MAX_VUS,
    startTime: `${startTimeSeconds}s`,
    gracefulStop: '0s',
    tags: {
      experiment: EXPERIMENT,
      endpoint: ENDPOINT,
      phase: 'measure',
      operation_type: operationType,
      target_rps: String(rate),
    },
  };
}

function measureTags(meta, operation, name) {
  return {
    name,
    experiment: EXPERIMENT,
    endpoint: ENDPOINT,
    phase: 'measure',
    operation_type: meta.operationType,
    target_rps: String(meta.rate),
    operation,
  };
}

function supportTags(operationType, operation, name) {
  return {
    name,
    experiment: EXPERIMENT,
    endpoint: ENDPOINT,
    phase: 'support',
    operation_type: 'support',
    support_for_operation_type: operationType,
    operation,
  };
}

function setupTags(operation, name) {
  return {
    name,
    experiment: EXPERIMENT,
    endpoint: ENDPOINT,
    phase: 'setup',
    operation_type: 'setup',
    operation,
  };
}

function shuffleIds(ids) {
  const result = [...ids];

  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = result[i];

    result[i] = result[j];
    result[j] = temp;
  }

  return result;
}

function authHeaders() {
  return {
    Authorization: `Token ${AUTH_TOKEN}`,
  };
}

function jsonHeaders() {
  return {
    ...authHeaders(),
    'Content-Type': 'application/json',
  };
}

function requiredEnv(name) {
  const value = __ENV[name];

  if (value === undefined || value.trim() === '') {
    throw new Error(`Required environment variable ${name} is not set`);
  }

  return value;
}