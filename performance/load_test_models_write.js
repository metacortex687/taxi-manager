import http from 'k6/http';
import { check } from 'k6';
import exec from 'k6/execution';

import {
  MODEL_PREFIX,
  MODEL_URL,
  SUMMARY_TREND_STATS,
  deleteTestData,
  jsonHeaders,
  measureTags,
  modelBody,
  scenario,
} from './models_common.js';

const EXPERIMENT = 'models_write_ladder';

const WRITE_RATES = [50,];
const DURATION_SECONDS = 61;

const PRE_ALLOCATED_VUS = 50;
const MAX_VUS = 200;

const scenarios = {};
const metaByScenario = {};

let startTimeSeconds = 0;
let offset = 0;

for (const rate of WRITE_RATES) {
  const name = `write_${rate}_rps`;
  const count = rate * DURATION_SECONDS;

  metaByScenario[name] = {
    rate,
    offset,
    count,
  };

  scenarios[name] = scenario(
    'write',
    rate,
    DURATION_SECONDS,
    startTimeSeconds,
    EXPERIMENT,
    PRE_ALLOCATED_VUS,
    MAX_VUS,
  );

  startTimeSeconds += DURATION_SECONDS;
  offset += count;
}

export const options = {
  setupTimeout: '30m',
  teardownTimeout: '30m',
  scenarios,
  summaryTrendStats: SUMMARY_TREND_STATS,
  thresholds: {
    'http_req_failed{phase:measure}': ['rate<0.05'],
  },
};

export function setup() {
  deleteTestData(EXPERIMENT);
}

export default function () {
  const meta = metaByScenario[exec.scenario.name];
  const iteration = exec.scenario.iterationInTest;

  if (iteration >= meta.count) {
    return;
  }

  const modelNumber = meta.offset + iteration + 1;
  const name = `${MODEL_PREFIX}${modelNumber}`;

  const response = http.post(
    MODEL_URL,
    JSON.stringify(modelBody(name)),
    {
      headers: jsonHeaders(),
      tags: measureTags(EXPERIMENT, 'write', meta.rate, 'create_model', 'POST /api/v1/models/'),
    },
  );

  check(response, {
    'create status is 201': (r) => r.status === 201,
  });
}