import http from 'k6/http';
import { check } from 'k6';

// ========================
// Учебная настройка теста
// ========================

const RATES = [10, 20, 30, 50, 100, 150, 200, 220, 240];

const DURATION_SECONDS = 60;
const WARMUP_DURATION_SECONDS = 10;
const WARMUP_RATE = 50;
const TIME_UNIT = '1s';

const PRE_ALLOCATED_VUS = 20;
const MAX_VUS = 100;

const EXPERIMENT = 'latency_by_rps';
const ENDPOINT_NAME = 'trip_points';

// URL и токен лучше оставить в .load-testing.env,
// чтобы не хранить секреты в JS-файле.
const BASE_URL = requiredEnv('TARGET_BASE_URL');
const TARGET_PATH = requiredEnv('TARGET_PATH');
const AUTH_TOKEN = requiredEnv('AUTH_TOKEN');


// ========================
// Вспомогательная функция
// ========================

function requiredEnv(name) {
  const value = __ENV[name];

  if (value === undefined || value.trim() === '') {
    throw new Error(`Required environment variable ${name} is not set`);
  }

  return value;
}


// ========================
// Сценарии k6
// ========================

const scenarios = {};

scenarios['warmup_once'] = {
  executor: 'constant-arrival-rate',
  rate: WARMUP_RATE,
  timeUnit: TIME_UNIT,
  duration: `${WARMUP_DURATION_SECONDS}s`,
  preAllocatedVUs: PRE_ALLOCATED_VUS,
  maxVUs: MAX_VUS,
  startTime: '0s',
  gracefulStop: '0s',
  tags: {
    experiment: EXPERIMENT,
    endpoint: ENDPOINT_NAME,
    phase: 'warmup',
    target_rps: String(WARMUP_RATE),
  },
};

let startTimeSeconds = WARMUP_DURATION_SECONDS;

for (const rate of RATES) {
  scenarios[`measure_${rate}_rps`] = {
    executor: 'constant-arrival-rate',
    rate: rate,
    timeUnit: TIME_UNIT,
    duration: `${DURATION_SECONDS}s`,
    preAllocatedVUs: PRE_ALLOCATED_VUS,
    maxVUs: MAX_VUS,
    startTime: `${startTimeSeconds}s`,
    gracefulStop: '0s',
    tags: {
      experiment: EXPERIMENT,
      endpoint: ENDPOINT_NAME,
      phase: 'measure',
      target_rps: String(rate),
    },
  };

  startTimeSeconds += DURATION_SECONDS;
}

export const options = {
  scenarios: scenarios,

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
    http_req_failed: ['rate<0.9'],
  },
};


// ========================
// Сам HTTP-запрос
// ========================

export default function () {
  const response = http.get(`${BASE_URL}${TARGET_PATH}`, {
    headers: {
      Authorization: `Token ${AUTH_TOKEN}`,
    },
  });

  check(response, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });
}