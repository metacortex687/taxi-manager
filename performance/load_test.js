import http from 'k6/http';
import { check, sleep } from 'k6';

const vus = Number(__ENV.VUS || '1');
const iterations = Number(__ENV.ITERATIONS || '100');
const sleepSeconds = Number(__ENV.SLEEP || '0');

export const options = {
  scenarios: {
    ab_equivalent: {
      executor: 'shared-iterations',
      vus: vus,
      iterations: iterations,
      maxDuration: __ENV.MAX_DURATION || '5m',
    },
  },

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
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const baseUrl = __ENV.TARGET_BASE_URL || 'http://nginx';
  const targetPath = __ENV.TARGET_PATH || '/';
  const token = __ENV.AUTH_TOKEN || '';

  const params = {
    headers: {},
  };

  if (token) {
    params.headers.Authorization = `Token ${token}`;
  }

  const response = http.get(`${baseUrl}${targetPath}`, params);

  check(response, {
    'status is 2xx': (r) => r.status >= 200 && r.status < 300,
  });

  if (sleepSeconds > 0) {
    sleep(sleepSeconds);
  }
}