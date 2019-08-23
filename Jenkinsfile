pipeline {
    agent {
        dockerfile {
            filename 'Dockerfile'
            args  '-v /etc/passwd:/etc/passwd'
        }
    }
    options {
      disableConcurrentBuilds()
      lock resource: 'jenkins_sdwan'
    }
    environment {
        VIRL_USERNAME = credentials('cpn-virl-username')
        VIRL_PASSWORD = credentials('cpn-virl-password')
        VIRL_HOST = credentials('cpn-virl-host')
        VIRL_SESSION = "jenkins_workshop1"
        VIPTELA_ORG = "DevNet Learning Lab"
        HOME = "${WORKSPACE}"
        DEFAULT_LOCAL_TMP = "${WORKSPACE}/ansible"
    }
    stages {
        stage('Build VIRL Topology') {
           steps {
                echo 'Running build.yml...'
                ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', playbook: 'build.yml'
           }
        }
        stage('Configure SD-WAN Fabric') {
           steps {
                echo 'Configure SD-WAN Fabric'
                withCredentials([file(credentialsId: 'viptela-serial-file', variable: 'VIPTELA_SERIAL_FILE')]) {
                    ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', extras: '-e virl_tag=jenkins -e \'organization_name="${VIPTELA_ORG}"\' -e serial_number_file=${VIPTELA_SERIAL_FILE} -e viptela_cert_dir=${WORKSPACE}/myCA', playbook: 'configure.yml'
                }
                echo 'Loading Templates...'
                ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', playbook: 'import-templates.yml'
                echo 'Waiting for vEdges to Sync...'
                ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', playbook: 'waitfor-sync.yml'
                echo 'Attaching Templates...'
                ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', playbook: 'attach-template.yml'
           }
        }
        stage('Running Tests') {
           steps {
                echo 'Check SD-WAN...'
                ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', playbook: 'check-sdwan.yml'
           }
        }      
    }    
    post {
        always {
            ansiblePlaybook disableHostKeyChecking: true, inventory: 'inventory/', playbook: 'clean.yml'
            cleanWs()
        }
    }
}