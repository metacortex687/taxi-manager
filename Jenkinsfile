pipeline {
    agent any

    environment {
        APP_IMAGE   = "taxi-manager-ci:${BUILD_NUMBER}"
        DB_CONTAINER = "taxi-manager-ci-db-${BUILD_NUMBER}"
        CI_NETWORK   = "taxi-manager-ci-${BUILD_NUMBER}"

        POSTGRES_DB       = "taxi_manager"
        POSTGRES_USER     = "postgres"
        POSTGRES_PASSWORD = "postgres"
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

                    mkdir -p reports

                    set +e

                    docker run \
                        --name "$TEST_CONTAINER" \
                        --network "$CI_NETWORK" \
                        -e DATABASE_URL="postgis://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}" \
                        -e SECRET_KEY="jenkins-test-secret-key" \
                        -e LOCATIONIQ_KEY="" \
                        -e TEST_OUTPUT_DIR="/reports" \
                        "$APP_IMAGE" \
                        uv run manage.py test

                    TEST_EXIT_CODE=$?

                    docker cp "$TEST_CONTAINER:/reports/." reports/
                    docker rm "$TEST_CONTAINER"

                    exit "$TEST_EXIT_CODE"
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/*.xml',
                allowEmptyResults: true

            sh '''
                docker rm -f "$TEST_CONTAINER" 2>/dev/null || true
                docker rm -f "$DB_CONTAINER" 2>/dev/null || true
                docker network rm "$CI_NETWORK" 2>/dev/null || true
                docker image rm "$APP_IMAGE" 2>/dev/null || true
            '''
    }
}


}