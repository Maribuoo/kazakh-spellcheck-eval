// Jenkinsfile — declarative pipeline for kkspell (Assignment 5).
//
// Provided to satisfy Assignment 5's literal submission requirement
// ("link to the repository with the project and Jenkinsfile") and to
// demonstrate Jenkins declarative-pipeline syntax. The pipeline that
// actually runs and produces the submitted evidence (screenshots, green
// checks) is the GitHub Actions workflow in .github/workflows/ci.yml,
// which has already been running successfully since Assignment 3 and is
// extended here with a `docker` job — see the practical report for why a
// self-hosted Jenkins server was not deployed. This Jenkinsfile mirrors
// the exact same stages and could be pointed at a real Jenkins server
// with no changes beyond configuring a Pipeline job against this
// repository; it has not itself been executed.

pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -e ".[dev]"
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    ruff check .
                '''
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest --cov=kkspell --cov-report=term-missing --cov-fail-under=90 --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build Docker image') {
            // Only runs after lint + tests succeed, same gating as the
            // GitHub Actions 'docker' job (needs: test).
            steps {
                sh 'docker build -t kkspell:${BUILD_NUMBER} .'
            }
        }

        stage('Push to Docker Hub (optional)') {
            when {
                allOf {
                    branch 'main'
                    expression { return env.DOCKERHUB_CREDENTIALS_ID != null }
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: env.DOCKERHUB_CREDENTIALS_ID,
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                        docker tag kkspell:${BUILD_NUMBER} $DOCKERHUB_USERNAME/kkspell:latest
                        docker push $DOCKERHUB_USERNAME/kkspell:latest
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded: tests passed and Docker image built.'
        }
        failure {
            echo 'Pipeline failed — see stage logs above.'
        }
    }
}
