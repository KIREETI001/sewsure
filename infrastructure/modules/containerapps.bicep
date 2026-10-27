// Container Apps environment, the API app and a manually triggered Job
// (migrations, batch AI evaluation). Both run as the shared managed identity.
param environmentName string
param apiAppName string
param jobName string
param location string
param tags object = {}

param logAnalyticsName string
param identityId string
param identityClientId string
param registryLoginServer string

@description('Placeholder until the first api deploy; azd replaces it.')
param apiImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
param apiTargetPort int = 80
param apiMinReplicas int = 0
param apiMaxReplicas int = 2
param apiCpu string = '0.5'
param apiMemory string = '1Gi'

@description('Plain, non-secret settings passed to the API and Job. Secrets are read from Key Vault by the app.')
param env array = []

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsName
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiAppName
  location: location
  tags: union(tags, {
    'azd-service-name': 'api'
  })
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: apiTargetPort
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: registryLoginServer
          identity: identityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          resources: {
            cpu: json(apiCpu)
            memory: apiMemory
          }
          env: env
        }
      ]
      scale: {
        minReplicas: apiMinReplicas
        maxReplicas: apiMaxReplicas
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
}

resource job 'Microsoft.App/jobs@2024-03-01' = {
  name: jobName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identityId}': {}
    }
  }
  properties: {
    environmentId: environment.id
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 1800
      replicaRetryLimit: 0
      manualTriggerConfig: {
        parallelism: 1
        replicaCompletionCount: 1
      }
      registries: [
        {
          server: registryLoginServer
          identity: identityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'job'
          image: apiImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: union(env, [
            {
              name: 'AZURE_CLIENT_ID'
              value: identityClientId
            }
          ])
        }
      ]
    }
  }
}

output environmentId string = environment.id
output apiName string = api.name
output apiFqdn string = api.properties.configuration.ingress.fqdn
output jobName string = job.name
