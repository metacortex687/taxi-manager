pipeline {
    agent any

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
                sh 'ls -la'
            }
        }
    }
}