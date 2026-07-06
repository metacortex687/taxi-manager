import http from 'k6/http';
import { check, fail } from 'k6';
import exec from 'k6/execution';

import {
  MODEL_URL,
  SUMMARY_TREND_STATS,
  authHeaders,
  loadModelIdsByHeavyList,
  logIds,
  measureTags,
  scenario,
} from './models_common.js';

const EXPERIMENT = 'models_read_ladder';

const READ_RATES = [50,100,150,200,250];
const DURATION_SECONDS = 61;

const PRE_ALLOCATED_VUS = 50;
const MAX_VUS = 200;

const scenarios = {};
const metaByScenario = {};

let startTimeSeconds = 0;

for (const rate of READ_RATES) {
  const name = `read_${rate}_rps`;

  metaByScenario[name] = {
    rate,
  };

  scenarios[name] = scenario(
    'read',
    rate,
    DURATION_SECONDS,
    startTimeSeconds,
    EXPERIMENT,
    PRE_ALLOCATED_VUS,
    MAX_VUS,
  );

  startTimeSeconds += DURATION_SECONDS;
}

export const options = {
  setupTimeout: '30m',
  teardownTimeout: '5m',
  scenarios,
  summaryTrendStats: SUMMARY_TREND_STATS,
  thresholds: {
    'http_req_failed{phase:measure}': ['rate<0.05'],
  },
};

export function setup() {
  const ids = loadModelIdsByHeavyList(EXPERIMENT);
  logIds('Loaded read ids by heavy list', ids);

  return { ids };
}

export default function (data) {
  if (!data || !data.ids || data.ids.length === 0) {
    fail('Нет ids для read-теста.');
  }

  const meta = metaByScenario[exec.scenario.name];
  const index = exec.scenario.iterationInTest % data.ids.length;
  const modelId = data.ids[index];
  const cycle = Math.floor(exec.scenario.iterationInTest / data.ids.length) + 1;
  
  if (index === 0) {
    console.log(
        `Начался цикл чтения ids: ` +
        `scenario=${exec.scenario.name}, ` +
        `target_rps=${meta.rate}, ` +
        `cycle=${cycle}, ` +
        `ids_count=${data.ids.length}`,
    );
  }

  const response = http.get(
    `${MODEL_URL}${modelId}/`,
    {
      headers: authHeaders(),
      tags: {
        ...measureTags(EXPERIMENT, 'read', meta.rate, 'read_model', 'GET /api/v1/models/:id/'),
        cycle: String(cycle),
    },
    },
  );

  check(response, {
    'read status is 200': (r) => r.status === 200,
  });
}