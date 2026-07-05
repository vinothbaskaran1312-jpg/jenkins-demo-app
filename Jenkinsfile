pipeline {
    agent { label 'node2' }
    
    environment {
        DOCKER_IMAGE = 'vinothbaskaran1312/jenkins-demo-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code..."
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
        
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
            echo '✅ CI Pipeline done! ArgoCD will deploy to Kubernetes.'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
        always {
            sh 'docker logout || true'
        }
    }
}
