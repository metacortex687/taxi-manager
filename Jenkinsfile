pipeline {
    agent any

    environment {
        APP_IMAGE   = "taxi-manager-ci:${BUILD_NUMBER}"
        DB_CONTAINER = "taxi-manager-ci-db-${BUILD_NUMBER}"
        CI_NETWORK   = "taxi-manager-ci-${BUILD_NUMBER}"
        TEST_CONTAINER = "taxi-manager-ci-tests-${BUILD_NUMBER}"
        APP_CONTAINER = "taxi-manager-ci-app-${BUILD_NUMBER}"

        POSTGRES_DB       = "taxi_manager"
        POSTGRES_USER     = "postgres"
        POSTGRES_PASSWORD = "postgres"
        BASE_URL = "http://app:8000"
    }

    stages {

        stage('Check user') {
            steps {
                sh 'echo "Environment USER: $USER"'
                sh 'echo "Actual user: $(whoami)"'
            }
        }

        stage('Check repository') {
            steps {
                sh 'pwd'
                // sh 'ls -la'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build \
                        -t "$APP_IMAGE" \
                        .
                '''
            }
        }

        stage('Django tests') {
            steps {
                sh '''
                    set -e

                    docker network create "$CI_NETWORK"

                    docker run \
                        -d \
                        --name "$DB_CONTAINER" \
                        --network "$CI_NETWORK" \
                        --network-alias db \
                        -e POSTGRES_DB="$POSTGRES_DB" \
                        -e POSTGRES_USER="$POSTGRES_USER" \
                        -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
                        postgis/postgis:16-3.5

                    until docker exec "$DB_CONTAINER" \
                        pg_isready \
                        -U "$POSTGRES_USER" \
                        -d "$POSTGRES_DB"
                    do
                        sleep 2
                    done

                    rm -rf reports
                    mkdir -p reports

                    TEST_EXIT_CODE=0

                    docker run \
                        --name "$TEST_CONTAINER" \
                        --network "$CI_NETWORK" \
                        -e DATABASE_URL="postgis://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}" \
                        -e SECRET_KEY="jenkins-test-secret-key" \
                        -e LOCATIONIQ_KEY="" \
                        -e TEST_OUTPUT_DIR="/reports" \
                        "$APP_IMAGE" \
                        uv run manage.py test \
                        || TEST_EXIT_CODE=$?

                    echo "Копирование XML-отчётов из $TEST_CONTAINER"

                    docker cp \
                        "$TEST_CONTAINER:/reports/." \
                        reports/

                    echo "Найденные XML-отчёты:"
                    find reports -type f -name "*.xml" -print

                    exit "$TEST_EXIT_CODE"
                '''
            }
        }

        stage('Start demo application') {
            steps {
                sh '''
                    docker run -d \
                        --name "$APP_CONTAINER" \
                        --network "$CI_NETWORK" \
                        --network-alias app \
                        -e DATABASE_URL="postgis://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}" \
                        -e SECRET_KEY="jenkins-test-secret-key" \
                        -e LOCATIONIQ_KEY="" \
                        "$APP_IMAGE" \
                        sh -c "make migrate && make ensure-demo-data && make run-dev"

                    until docker exec "$APP_CONTAINER" \
                        uv run python -c \
                        'import socket; socket.create_connection(("127.0.0.1", 8000), 2).close()'
                    do
                        sleep 2
                    done
                '''
            }
        }



        stage('Playwright tests') {
            agent {
                docker {
                    image 'mcr.microsoft.com/playwright:v1.61.0-noble'
                    args "--ipc=host --network=${env.CI_NETWORK}"
                    reuseNode true
                }
            }

            steps {
                dir('playwright') {
                    sh '''
                        echo "Current directory:"
                        pwd
                        
                        echo "Files:"
                        ls -la
                        
                        node --version
                        npm --version

                        npm ci
                        npx playwright test
                    '''                    
                }
            }

            post {
                always {
                    archiveArtifacts(
                        artifacts: 'playwright/playwright-report/**',
                        allowEmptyArchive: true
                    )
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f "$APP_CONTAINER" 2>/dev/null || true
                docker rm -f "$TEST_CONTAINER" 2>/dev/null || true
                docker rm -f "$DB_CONTAINER" 2>/dev/null || true
                docker network rm "$CI_NETWORK" 2>/dev/null || true
                docker image rm "$APP_IMAGE" 2>/dev/null || true
            '''

            junit testResults: 'reports/**/*.xml',
                allowEmptyResults: false
        }
    }
}