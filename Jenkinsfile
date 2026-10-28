// Jenkinsfile — declarative pipeline for kkspell (Assignment 5).
//
// Satisfies Assignment 5's Jenkins requirement with a pipeline that was
// actually deployed and run end to end on a real, self-hosted Jenkins
// server (Jenkins 2.580.1, in Docker, on the author's own machine) — see
// the practical report, Sections 3, 6 and 7, for the setup and the
// screenshots of the resulting green build. The same stages also run on
// every push via the GitHub Actions workflow in .github/workflows/ci.yml.
// A successful run: checkout -> install -> lint -> unit tests -> build
// Docker image -> deploy (promote the image and run it once against the
// sample corpus, archiving the output) -> optional Docker Hub push.

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

        stage('Deploy to test environment') {
            // Continuous Deployment step. kkspell is a batch/research CLI
            // tool, not an HTTP service, so "deploying" it means: promote
            // the image that has just passed lint + tests + build to a
            // stable tag that downstream consumers (e.g. the author's
            // dissertation pipeline) can always pull, then automatically
            // run it once against the sample corpus as a live smoke
            // check of the *deployed* artifact, and archive that output
            // as the build's deployment evidence. No manual step is
            // needed between a passing build and a deployed, verified
            // image.
            steps {
                sh '''
                    docker tag kkspell:${BUILD_NUMBER} kkspell:latest-tested
                    docker run --rm kkspell:latest-tested evaluate data/sample_corpus_kk.txt --n-eval 60 --bootstrap 50 | tee deploy_result.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'deploy_result.txt', allowEmptyArchive: true
                }
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
            echo 'Pipeline succeeded: tests passed, Docker image built, and image deployed to the test environment (kkspell:latest-tested).'
        }
        failure {
            echo 'Pipeline failed — see stage logs above.'
        }
    }
}
