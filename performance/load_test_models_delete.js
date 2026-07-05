import http from 'k6/http';
import { check, fail } from 'k6';
import exec from 'k6/execution';

import {
  MODEL_URL,
  SUMMARY_TREND_STATS,
  authHeaders,
  deleteTestData,
  loadModelIdsByHeavyList,
  logIds,
  measureTags,
  scenario,
} from './models_common.js';

const EXPERIMENT = 'models_delete_ladder';

const DELETE_RATES = [10,];
const DURATION_SECONDS = 61;

const PRE_ALLOCATED_VUS = 50;
const MAX_VUS = 200;

const scenarios = {};
const metaByScenario = {};

let startTimeSeconds = 0;
let offset = 0;

for (const rate of DELETE_RATES) {
  const name = `delete_${rate}_rps`;
  const count = rate * DURATION_SECONDS;

  metaByScenario[name] = {
    rate,
    offset,
    count,
  };

  scenarios[name] = scenario(
    'delete',
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
  const ids = loadModelIdsByHeavyList(EXPERIMENT);
  logIds('Loaded delete ids by heavy list', ids);

  return { ids };
}

export default function (data) {
  if (!data || !data.ids || data.ids.length === 0) {
    fail('Нет ids для delete-теста.');
  }

  const meta = metaByScenario[exec.scenario.name];
  const index = meta.offset + exec.scenario.iterationInTest;

  if (index >= data.ids.length) {
    return;
  }

  const modelId = data.ids[index];

  const response = http.del(
    `${MODEL_URL}${modelId}/`,
    null,
    {
      headers: authHeaders(),
      tags: measureTags(EXPERIMENT, 'delete', meta.rate, 'delete_model', 'DELETE /api/v1/models/:id/'),
    },
  );

  check(response, {
    'delete status is 204': (r) => r.status === 204,
  });
}

export function teardown() {
  deleteTestData(EXPERIMENT);
}