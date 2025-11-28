pipeline {
    agent any
    options {
      timeout(time: 60, unit: 'MINUTES')
    }

    parameters {
      string(name: 'TARGET_BRANCH', defaultValue: 'origin/refactorCodeBase', description: 'Branch to diff against to detect changes (e.g., origin/main)')
      string(name: 'REGISTRY', defaultValue: '', description: 'Docker registry (leave empty for Docker Hub, e.g., docker.io)')
      string(name: 'ORG', defaultValue: 'reflection', description: 'Registry org/namespace')
    }

    environment {
      KUBECONFIG_CRED = 'kubeconfig-file'
      DB_CREDENTIALS = 'db-credentials'
      IMAGE_TAG = "${env.GIT_COMMIT ?: 'local-' + UUID.randomUUID().toString().take(8)}"
      NAMESPACE = 'reflection'
    }

    stages {
      stage('Checkout') {
        steps {
          checkout scm
          sh 'git fetch --all --prune'
        }
      }

      stage('Detect changed services') {
        steps {
          script {
            def changed = sh(script: "git diff --name-only HEAD~1 HEAD || true", returnStdout: true).trim()
            echo "Changed files:\n${changed}"

            def mapping = [
              'services/frontend'           : 'frontend',
              'services/login-management'   : 'login-management',
              'services/file-parsing'       : 'file-parsing',
              'services/question-answer-generation': 'qa-generation',
              'services/qa-generation'      : 'qa-generation',
              'services/speechtotext'       : 'speechtotext',
              'services/SpeechToText'       : 'speechtotext',
              'services/resources'          : 'resources',

              'k8s/deployments/frontend.yaml'        : 'frontend',
              'k8s/deployments/login-management.yaml': 'login-management',
              'k8s/deployments/file-parsing.yaml'    : 'file-parsing',
              'k8s/deployments/qa-generation.yaml'   : 'qa-generation',
              'k8s/deployments/speechtotext.yaml'    : 'speechtotext',
              'k8s/deployments/resources.yaml'       : 'resources'
            ]

            def changedServices = [] as Set
            if (changed) {
              changed.split('\\n').each { f ->
                mapping.each { path, svc ->
                  if (f.startsWith(path)) {
                    changedServices << svc
                  }
                }
              }
            }

            env.CHANGED_SERVICES = changedServices.join(',')
            if (!env.CHANGED_SERVICES) {
              echo "No service-level changes detected; pipeline will skip build/deploy stages."
            } else {
              echo "Services to build/deploy: ${env.CHANGED_SERVICES}"
            }
          }
        }
      }

      stage('Apply Configuration Changes') {
        steps {
          script {
            withCredentials([
              file(credentialsId: env.KUBECONFIG_CRED, variable: 'KUBECONFIG'),
              usernamePassword(credentialsId: env.DB_CREDENTIALS, usernameVariable: 'MONGO_USER', passwordVariable: 'MONGO_PASS')
            ]) {

              def configChanged = sh(
                script: "git diff --name-only HEAD~1 HEAD | grep -E 'k8s/configmap.yaml|k8s/.*-configmap.yaml' || true", 
                returnStdout: true
              ).trim()
              
              if (configChanged) {
                echo "Configuration changes detected: ${configChanged}"
                echo "Applying ConfigMap..."
                sh """
                  kubectl apply -f k8s/configmap.yaml -n ${env.NAMESPACE} || echo "ConfigMap apply failed"
                """
                
                def dbNameChanged = sh(
                  script: "git diff HEAD~1 HEAD k8s/configmap.yaml | grep 'DATABASE_NAME' || true",
                  returnStdout: true
                ).trim()
                
                if (dbNameChanged) {
                  echo "⚠️  DATABASE_NAME changed! Restarting services that use MongoDB..."
                  sh """
                    kubectl rollout restart deployment/login-management-deployment -n ${env.NAMESPACE} || true
                    echo "Services restarted to pick up new database name"
                  """
                  
                  echo "📊 Populating resources data in new database..."
                  sh """
                    MONGO_POD=\$(kubectl get pod -n ${env.NAMESPACE} -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
                    
                    if [ -z "\$MONGO_POD" ]; then
                      echo "❌ Could not find MongoDB pod"
                      exit 1
                    fi
                    
                  DB_NAME=\$(kubectl get configmap reflection-config -n ${env.NAMESPACE} -o jsonpath='{.data.DATABASE_NAME}')
                  echo "📝 Populating database: \$DB_NAME"
                  
                  kubectl cp services/resources/data.py ${env.NAMESPACE}/\$MONGO_POD:/tmp/data.py
                  
                  kubectl exec -n ${env.NAMESPACE} \$MONGO_POD -- bash -c "
                    apt-get update -qq > /dev/null 2>&1 && 
                    apt-get install -y python3-pip -qq > /dev/null 2>&1 && 
                    pip3 install pymongo --quiet > /dev/null 2>&1 &&
                    export MONGODB_URI='mongodb://${MONGO_USER}:${MONGO_PASS}@localhost:27017/' &&
                    export DATABASE_NAME='\$DB_NAME' &&
                    python3 /tmp/data.py
                  " 2>&1 | grep -v "debconf\\|WARNING\\|Collecting\\|Downloading\\|Installing" || true
                  
                  echo "✅ Resources data populated successfully!"
                """
              }
            } else {
              echo "No configuration changes detected"
            }

          } // end withCredentials
        }   // end script
      }     // end steps
    }       // end stage

      stage('Build & Deploy changed services') {
        when {
          expression { return env.CHANGED_SERVICES?.trim() }
        }
        steps {
          script {
            withCredentials([file(credentialsId: env.KUBECONFIG_CRED, variable: 'KUBECONFIG')]) {

              def services = env.CHANGED_SERVICES.tokenize(',')
              
              def serviceDirMap = [
                'qa-generation': 'question-answer-generation',
                'speechtotext': 'SpeechToText',
                'frontend': 'frontend',
                'login-management': 'login-management',
                'file-parsing': 'file-parsing',
                'resources': 'resources'
              ]
              
              for (svc in services) {
                  if (!svc) { continue }
                  def image = "${params.ORG}/${svc}:${env.IMAGE_TAG}"
                  def actualDir = serviceDirMap[svc] ?: svc
                  def dockerfileDir = "services"
                  def k8sManifest = "k8s/deployments/${svc}.yaml"

                  stage("Build ${svc}") {
                    sh """
                      echo "Building ${svc} -> ${image}"
                      docker build --file ${dockerfileDir}/${actualDir}/Dockerfile -t ${image} ${dockerfileDir}
                      echo "Image built successfully: ${image}"
                    """
                  }

                  stage("Deploy ${svc}") {
                    sh """
                      tmp=\$(mktemp /tmp/${svc}-manifest.XXXX.yaml)
                      awk -v img="${image}" '{
                        if (!found && match(\$0,/^[[:space:]]*image:[[:space:]]*/)) {
                          sub(/^[[:space:]]*image:[[:space:]]*.*/, "        image: " img)
                          found=1
                        }
                        print
                      }' ${k8sManifest} > \$tmp

                      kubectl apply -f \$tmp -n ${env.NAMESPACE}
                      rm -f \$tmp

                      kubectl rollout status deployment/${svc}-deployment -n ${env.NAMESPACE} --timeout=120s || true
                    """
                  }
                }
            }
          }
        }
      }
    }

    post {
      success {
        echo "Pipeline finished successfully. Services changed: ${env.CHANGED_SERVICES ?: 'none'}"
        script {
          sh '''
            echo "Restarting port-forwards for local user..."
            sudo -u lightning bash -c "cd /home/lightning/Desktop/Study/7th_sem/capstone2/Reflection/Reflection && ./start-ingress.sh" || echo "Port-forward restart failed, run './start-ingress.sh' manually"
          '''
        }
      }
      failure {
        echo "Pipeline failed. See console logs for details."
      }
      cleanup {
        echo "Cleanup if required."
      }
    }
}
