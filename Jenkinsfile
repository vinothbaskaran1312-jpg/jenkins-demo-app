pipeline {
    agent { label 'node2' }
    
    environment {
        DOCKER_IMAGE = 'vinothbaskaran1985/jenkins-demo-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code..."
                checkout scm
                echo "Commit: ${env.GIT_COMMIT}"
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running pytest tests..."
                sh """
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt --quiet
                    pytest test_app.py -v
                    deactivate
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }

       stage('Trivy Security Scan') {
    steps {
        echo "Scanning Docker image for vulnerabilities..."
        sh """
            # Create bin directory for jenkins user if not exists
            mkdir -p /home/jenkins/bin

            # Install Trivy if not already installed
            if ! command -v /home/jenkins/bin/trivy &> /dev/null; then
                echo "Installing Trivy..."
                curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /home/jenkins/bin
            else
                echo "Trivy already installed, skipping download..."
            fi

            # Run the scan
            /home/jenkins/bin/trivy image \
                --severity HIGH,CRITICAL \
                --exit-code 0 \
                --no-progress \
                ${DOCKER_IMAGE}:${DOCKER_TAG}
        """
    }
}
Key changes:

Uses /home/jenkins/bin/trivy (full path, no sudo needed)
Checks if already installed → skips download on subsequent builds (faster!)
--exit-code 0 means pipeline continues even if vulnerabilities found (we report but don't fail)

Save, then push:
bashgit add Jenkinsfile
git commit -m "Fix Trivy install - use jenkins user home directory"
git push origin main
Then Build Now in Jenkins — share the Console Output for the Trivy stage! 🚀

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Update Manifests') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-credentials',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh """
                        rm -rf jenkins-demo-manifests
                        git clone https://\${GIT_USER}:\${GIT_PASS}@github.com/vinothbaskaran1312-jpg/jenkins-demo-manifests.git
                        cd jenkins-demo-manifests
                        sed -i 's|${DOCKER_IMAGE}:.*|${DOCKER_IMAGE}:${DOCKER_TAG}|g' deployment.yaml
                        git config user.email "jenkins@node1"
                        git config user.name "Jenkins"
                        git add deployment.yaml
                        git commit -m "Update image tag to ${DOCKER_TAG} [skip ci]"
                        git push https://\${GIT_USER}:\${GIT_PASS}@github.com/vinothbaskaran1312-jpg/jenkins-demo-manifests.git main
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline complete! ArgoCD will deploy to Kubernetes.'
        }
        failure {
            echo '❌ Pipeline failed! Check logs above.'
        }
        always {
            sh 'docker logout || true'
            sh 'docker system prune -f || true'
            sh 'rm -rf venv || true'
        }
    }
}