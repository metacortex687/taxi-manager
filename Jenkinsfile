pipeline {
    agent any

    environment {
        COMPOSE_FILE         = 'compose.jenkins-ci.yaml'
        COMPOSE_PROJECT_NAME = "taxi-manager-ci-${BUILD_NUMBER}"
        TEST_CONTAINER       = "taxi-manager-ci-tests-${BUILD_NUMBER}"
        APP_IMAGE            = "taxi-manager-ci:${BUILD_NUMBER}"
        BASE_URL             = 'http://taxi-app:8000'
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
                        -e DJANGO_SETTINGS_MODULE=taxi_manager.settings_wsgi \
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
    }

    post {
        always {
            sh '''
                docker rm -f "$TEST_CONTAINER" 2>/dev/null || true
                docker compose down -v --remove-orphans || true
                docker image rm "$APP_IMAGE" 2>/dev/null || true
            '''
        }
    }
}