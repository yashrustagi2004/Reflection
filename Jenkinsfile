  pipeline {
    agent any
    options {
      // Keep logs, limit build time
      timeout(time: 60, unit: 'MINUTES')
    }

    parameters {
      string(name: 'TARGET_BRANCH', defaultValue: 'origin/refactorCodeBase', description: 'Branch to diff against to detect changes (e.g., origin/main)')
      string(name: 'REGISTRY', defaultValue: '', description: 'Docker registry (leave empty for Docker Hub, e.g., docker.io)')
      string(name: 'ORG', defaultValue: 'reflection', description: 'Registry org/namespace')
    }

    environment {
      // Jenkins credential ID - only kubeconfig needed for local deployment
      KUBECONFIG_CRED = 'kubeconfig-file'        // file credential
      // Tag images with commit SHA so each build is immutable
      IMAGE_TAG = "${env.GIT_COMMIT ?: 'local-' + UUID.randomUUID().toString().take(8)}"
      NAMESPACE = 'reflection'
    }

    stages {
      stage('Checkout') {
        steps {
          // checkout with full history (needed for git diff)
          checkout scm
          sh 'git fetch --all --prune'
        }
      }

      stage('Detect changed services') {
        steps {
          script {
            // Compute changed files relative to previous commit
            // Use HEAD~1 to compare with previous commit
            def changed = sh(script: "git diff --name-only HEAD~1 HEAD || true", returnStdout: true).trim()
            echo "Changed files:\n${changed}"

            // Configure path->service mapping
            def mapping = [
              'services/frontend'           : 'frontend',
              'services/login-management'   : 'login-management',
              'services/file-parsing'       : 'file-parsing',
              'services/question-answer-generation': 'qa-generation',
              'services/qa-generation'      : 'qa-generation',
              'services/speechtotext'       : 'speechtotext',
              'services/SpeechToText'       : 'speechtotext',
              'services/resources'          : 'resources',
              // k8s deployment files (if k8s yaml changed, redeploy corresponding service)
              'k8s/deployments/frontend.yaml'        : 'frontend',
              'k8s/deployments/login-management.yaml': 'login-management',
              'k8s/deployments/file-parsing.yaml'    : 'file-parsing',
              'k8s/deployments/qa-generation.yaml'   : 'qa-generation',
              'k8s/deployments/speechtotext.yaml'    : 'speechtotext',
              'k8s/deployments/resources.yaml'       : 'resources'
            ]

            // Decide changed services
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

            // Expose to later stages
            env.CHANGED_SERVICES = changedServices.join(',')
            if (!env.CHANGED_SERVICES) {
              echo "No service-level changes detected; pipeline will skip build/deploy stages."
            } else {
              echo "Services to build/deploy: ${env.CHANGED_SERVICES}"
            }
          }
        }
      }

      stage('Build & Deploy changed services') {
        when {
          expression { return env.CHANGED_SERVICES?.trim() }
        }
        steps {
          script {
            // Prepare an array
            def services = env.CHANGED_SERVICES.tokenize(',')
            
            // Loop per service - kubectl will use Jenkins user's default kubeconfig
            for (svc in services) {
                if (!svc) { continue }
                def image = "${params.ORG}/${svc}:${env.IMAGE_TAG}"
                def dockerfileDir = "services/${svc}"
                def k8sManifest = "k8s/deployments/${svc}.yaml"

                stage("Build ${svc}") {
                  // Build the image locally (no push to registry)
                  sh """
                    echo "Building ${svc} -> ${image}"
                    docker build --file ${dockerfileDir}/Dockerfile -t ${image} ${dockerfileDir}
                    echo "Image built successfully: ${image}"
                  """
                }

                stage("Deploy ${svc}") {
                  // Create a temporary adjusted manifest that points to the new image and apply it
                  sh """
                    tmp=\$(mktemp /tmp/${svc}-manifest.XXXX.yaml)
                    # Safely replace the image line in the manifest. This is intentionally conservative:
                    # - it finds the first 'image:' in the file and substitutes the value. Adjust if your manifest has multiple images.
                    awk -v img="${image}" '{
                      if (!found && match(\$0,/^[[:space:]]*image:[[:space:]]*/)) {
                        sub(/^[[:space:]]*image:[[:space:]]*.*/, \"        image: \" img)
                        found=1
                      }
                      print
                    }' ${k8sManifest} > \$tmp
                    # Apply the temporary manifest - kubectl will use Jenkins user's kubeconfig
                    kubectl apply -f \$tmp -n ${env.NAMESPACE}
                    rm -f \$tmp
                    # Wait for rollout to complete
                    kubectl rollout status deployment/${svc}-deployment -n ${env.NAMESPACE} --timeout=120s || true
                  """
                }
              } // end for
          } // end script
        } // end steps
      } // end stage

      stage('Optional: Security scan') {
        when {
          expression { return params.SCAN == 'true' }
        }
        steps {
          echo "Optional vulnerability scan stage. Configure trivy or your scanner of choice and bind its credentials securely."
        }
      }
    } // end stages

    post {
      success {
        echo "Pipeline finished successfully. Services changed: ${env.CHANGED_SERVICES ?: 'none'}"
      }
      failure {
        echo "Pipeline failed. See console logs for details."
      }
      cleanup {
        echo "Cleanup if required."
      }
    }
  }
