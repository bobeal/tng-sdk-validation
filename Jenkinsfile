pipeline {
  agent any
  stages {
    stage('Container Build') {
      steps {
        echo 'Building..'
        sh 'docker build --no-cache -f ./Dockerfile -t registry.sonata-nfv.eu:5000/tng-sdk-validation .'
      }
    }
    stage('Unit Tests') {
      steps {
        echo 'Unit Testing..'
        sh "docker container ls -a | grep redis_docker && docker rm -f redis_docker || true"
        sh "docker network ls | grep redis_network && docker network rm redis_network || true"
        sh "docker network create --driver bridge redis_network"
        sh "docker run -d --name redis_docker -p 6379:6379 --network redis_network redis"
        sh "docker run --network redis_network -e VAPI_REDIS_HOST='redis_docker' -i --rm registry.sonata-nfv.eu:5000/tng-sdk-validation pytest -v --ignore=src/tngsdk/validation/gui/"
        sh "docker rm -f redis_docker || true"
        sh "docker network rm redis_network || true"
      }
    }
    stage('Code Style check') {
      steps {
        echo 'Checking code style....'
        sh "pipeline/checkstyle/check.sh"
      }
    }
    stage('Integration tests (SDK-tools)') {
        steps {
            echo 'Stage: Integration tests (SDK-tools)'
            sh "docker run --rm --name tng-sdk-validation-int registry.sonata-nfv.eu:5000/tng-sdk-validation pipeline/test/test_sdk_integration.sh"
        }
    }
    stage ("Downstream jobs: Trigger tng-sdk-package build") {
        when{
            branch 'master'
        }
        steps {
            build job: '../tng-sdk-package-pipeline/master', wait: true
        }
    }
    stage('Containers Publication') {
      steps {
        echo 'Publication of containers in local registry....'
      }
    }
    stage('Deployment in Integration') {
      steps {
        echo 'Deploying in integration...'
      }
    }
    stage('Smoke Tests') {
      steps {
        echo 'Performing Smoke Tests....'
      }
    }
    stage('Publish Results') {
      steps {
        echo 'Publish Results...'
      }
    }
  }
}
