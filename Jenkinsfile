pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: ansible
    image: jasonking/ansible-sdwan
    command:
    - sleep
    args:
    - 99d
    tty: true
"""
    }
  }
  options {
    disableConcurrentBuilds()
    lock resource: 'jenkins_virl1_sdwan'
  }
  environment {
    VIRL_USERNAME = credentials('cpn-virl-username')
    VIRL_PASSWORD = credentials('cpn-virl-password')
    VIRL_HOST = credentials('cpn-virl1-host')
    VIRL_SESSION = "jenkins_sdwan"
    HOME = "${WORKSPACE}"
    DEFAULT_LOCAL_TMP = "${WORKSPACE}/ansible"
  }
  stages {
    stage('Clean Previous Deployment') {
      steps {
        echo 'Running clean.yml...'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'clean.yml'
        }      
      }          
    }
    stage('Build Topology') {
      steps {
        echo 'Running build.yml...'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'build.yml'
        }
      }
    }
    stage('Configure Control Plane') {
      steps {
        echo 'Running configure.yml...'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'configure.yml'
        }
      }
    }
    stage('Import Templates') {
      steps {
        echo 'Running import-templates.yml'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'import-templates.yml'
        }
      }
    }
    stage('Wait for Edges') {
      steps {
        echo 'Running waitfor-sync.yml...'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'waitfor-sync.yml'
        }
      }
    }
    stage('Attach Templates') {
      steps {
        echo 'Running attach-template.yml'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'attach-template.yml'
        }
      }
    }
    stage('Run Tests') {
      steps {
        echo 'Running check-sdwan.yml...'
        container('ansible') {
          ansiblePlaybook disableHostKeyChecking: true, playbook: 'check-sdwan.yml'
        }
      }
    }
  }
  post {
    always {
      echo 'Cleaning up...'
      container('ansible') {
        ansiblePlaybook disableHostKeyChecking: true, playbook: 'clean.yml'
      }
      cleanWs()
    }
  }
}

