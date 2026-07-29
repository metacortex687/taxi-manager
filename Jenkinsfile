pipeline {
    agent {
        label 'slave'
    }

    environment {
        COMPOSE_FILE         = 'compose.jenkins-ci.yaml'
        COMPOSE_PROJECT_NAME = "taxi-manager-ci-${BUILD_NUMBER}"
        TEST_CONTAINER       = "taxi-manager-ci-tests-${BUILD_NUMBER}"
        APP_IMAGE            = "taxi-manager-ci:${BUILD_NUMBER}"
        BASE_URL             = 'http://taxi-app:8000'
        TEMPO_URL            = 'http://tempo:3200'
        DEPLOY_COMPOSE_FILE  = 'compose.deploy.yaml'
        DEPLOY_PROJECT_NAME  = 'taxi-manager-deploy'
    }

    stages {
        stage('Build') {
            steps {
                sh 'docker compose build taxi-app'
            }
        }

        stage('Django tests') {
            steps {
                sh '''
                    set -e

                    rm -rf reports
                    mkdir -p reports

                    docker compose up -d --wait db

                    TEST_EXIT_CODE=0

                    docker compose run \
                        --name "$TEST_CONTAINER" \
                        --no-deps \
                        -e "OTEL_RESOURCE_ATTRIBUTES=build=${BUILD_TAG},suite=django" \
                        taxi-app \
                        sh -c 'mkdir -p /reports && exec uv run opentelemetry-instrument python manage.py test' \
                        || TEST_EXIT_CODE=$?

                    if docker inspect "$TEST_CONTAINER" >/dev/null 2>&1
                    then
                        docker cp "$TEST_CONTAINER:/reports/." reports/ || true
                        docker rm -f "$TEST_CONTAINER"
                    fi

                    exit "$TEST_EXIT_CODE"
                '''
            }

            post {
                always {
                    junit testResults: 'reports/**/*.xml',
                        allowEmptyResults: true
                }
            }
        }

        stage('Check N+1') {
            agent {
                label 'master'
            }

            steps {
                sh '''
                    set -e
                    sleep 10

                    RESULT=$(curl -fsS --get "${TEMPO_URL}/api/search" \
                        --data-urlencode "q={ resource.service.name = \\"taxi-manager-ci\\" && resource.build = \\"${BUILD_TAG}\\" && span:kind = server }" \
                        --data-urlencode "limit=20")

                    printf '%s' "$RESULT" | grep -q '"traceID"' || {
                        echo "Трейсы сборки ${BUILD_TAG} не найдены"
                        exit 1
                    }

                    RESULT=$(curl -fsS --get "${TEMPO_URL}/api/search" \
                        --data-urlencode "q={ resource.service.name = \\"taxi-manager-ci\\" && resource.build = \\"${BUILD_TAG}\\" && span:kind = server } >> { resource.service.name = \\"taxi-manager-ci\\" && resource.build = \\"${BUILD_TAG}\\" && span:name =~ \\"SELECT.*\\" && span.db.statement != nil } | by(span.db.statement) | count() > 2" \
                        --data-urlencode "limit=20")

                    if printf '%s' "$RESULT" | grep -q '"traceID"'; then
                        echo "Обнаружена возможная проблема N+1"
                        printf '%s\n' "$RESULT"
                        exit 1
                    fi

                    echo "N+1 не обнаружен"
                '''
            }
        }

        stage('Fill demo data') {
            steps {
                sh '''
                    docker compose run --rm --no-deps \
                        taxi-app \
                        sh -c 'make migrate && make ensure-demo-data'
                '''
            }
        }

        stage('Start application') {
            steps {
                sh 'docker compose up -d --wait taxi-app'
            }
        }

        stage('Playwright tests') {
            agent {
                docker {
                    image 'mcr.microsoft.com/playwright:v1.61.0-noble'
                    args "--ipc=host --network=${env.COMPOSE_PROJECT_NAME}_default"
                    reuseNode true
                }
            }

            steps {
                dir('playwright') {
                    sh '''
                        npm ci
                        npx playwright test
                    '''
                }
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'playwright/playwright-report/**,playwright/test-results/**',
                        allowEmptyArchive: true
                    )
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    set -e

                    export DEPLOY_COMMIT_HASH="$(git rev-parse HEAD)"
                    export DEPLOY_COMMIT_TIME="$(git show -s --format=%cI HEAD)"
                    export DEPLOY_TIME="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

                    deploy() {
                        docker compose \
                            -p "$DEPLOY_PROJECT_NAME" \
                            -f "$COMPOSE_FILE" \
                            -f "$DEPLOY_COMPOSE_FILE" \
                            "$@"
                    }

                    deploy up -d --wait --no-build db

                    deploy run --rm --no-deps \
                        taxi-app \
                        sh -c 'make migrate && make ensure-demo-data'

                    deploy up -d --wait --no-build taxi-app nginx

                    echo "Приложение доступно на порту 8080"
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f "$TEST_CONTAINER" 2>/dev/null || true
                docker compose down -v --remove-orphans || true
                docker image rm "$APP_IMAGE" 2>/dev/null || true
                docker builder prune -af || true
                docker container prune -f || true
                docker image prune -af || true
            '''
        }
    }
}
