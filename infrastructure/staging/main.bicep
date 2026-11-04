// SewSure staging environment. Deploys into an existing resource group
// (a human creates it; see infrastructure/RUNBOOK.md).
targetScope = 'resourceGroup'

@minLength(2)
@maxLength(12)
@description('Short environment name, used in resource names. azd sets AZURE_ENV_NAME.')
param environmentName string = 'staging'

@description('Primary region. Check Postgres B1ms and Container Apps capacity for the subscription.')
param location string = resourceGroup().location

@description('Region for the Static Web App (limited set of regions).')
param staticWebAppLocation string = 'eastasia'

@description('Monthly budget for this resource group.')
param budgetAmount string = '50'

@description('Who receives budget alerts. Set by the human running the deployment.')
param budgetContactEmails array

@description('Container port the API listens on. The placeholder image listens on 80; set to the API port once services/api has a Dockerfile.')
param apiTargetPort string = '80'

@description('Image for the API and Job. azd replaces it on deploy.')
param apiImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Sign-in provider token issuer. The API rejects every request until all three auth values are set.')
param authIssuer string = ''

@description('Audience the API expects in sign-in tokens.')
param authAudience string = ''

@description('URL of the sign-in provider public keys (JWKS).')
param authJwksUrl string = ''

var tags = {
  project: 'sewsure'
  environment: environmentName
  'managed-by': 'azd'
}

// Stable per resource group + environment, short enough for storage/ACR/Key Vault limits.
var token = toLower(uniqueString(subscription().id, resourceGroup().id, environmentName))
var prefix = 'sewsure-${environmentName}'
var compact = 'sewsure${take(toLower(replace(environmentName, '-', '')), 6)}${take(token, 8)}'

module identity '../modules/identity.bicep' = {
  name: 'identity'
  params: {
    name: 'id-${prefix}'
    location: location
    tags: tags
  }
}

module monitoring '../modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    logAnalyticsName: 'log-${prefix}'
    appInsightsName: 'appi-${prefix}'
    location: location
    tags: tags
  }
}

module keyVault '../modules/keyvault.bicep' = {
  name: 'keyvault'
  params: {
    name: take('kv-${compact}', 24)
    location: location
    tags: tags
    secretsReaderPrincipalId: identity.outputs.principalId
  }
}

module storage '../modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: take('st${compact}', 24)
    location: location
    tags: tags
    blobContributorPrincipalId: identity.outputs.principalId
  }
}

module postgres '../modules/postgres.bicep' = {
  name: 'postgres'
  params: {
    name: 'psql-${prefix}-${take(token, 6)}'
    location: location
    tags: tags
    adminIdentityPrincipalId: identity.outputs.principalId
    adminIdentityName: identity.outputs.name
  }
}

module registry '../modules/registry.bicep' = {
  name: 'registry'
  params: {
    name: take('cr${compact}', 50)
    location: location
    tags: tags
    pullPrincipalId: identity.outputs.principalId
  }
}

module containerApps '../modules/containerapps.bicep' = {
  name: 'containerapps'
  params: {
    environmentName: 'cae-${prefix}'
    apiAppName: 'ca-api-${prefix}'
    jobName: 'caj-${prefix}'
    location: location
    tags: tags
    logAnalyticsName: monitoring.outputs.logAnalyticsName
    identityId: identity.outputs.id
    identityClientId: identity.outputs.clientId
    registryLoginServer: registry.outputs.loginServer
    apiImage: apiImage
    apiTargetPort: int(apiTargetPort)
    // Non-secret settings only. Model keys are read from Key Vault by the app.
    env: [
      { name: 'AZURE_CLIENT_ID', value: identity.outputs.clientId }
      { name: 'KEY_VAULT_URI', value: keyVault.outputs.uri }
      { name: 'BLOB_ENDPOINT', value: storage.outputs.blobEndpoint }
      { name: 'SEWSURE_POSTGRES_HOST', value: postgres.outputs.fqdn }
      { name: 'SEWSURE_POSTGRES_DB', value: postgres.outputs.databaseName }
      { name: 'SEWSURE_POSTGRES_USER', value: identity.outputs.name }
      { name: 'SEWSURE_MANAGED_IDENTITY_CLIENT_ID', value: identity.outputs.clientId }
      { name: 'SEWSURE_AUTH_ISSUER', value: authIssuer }
      { name: 'SEWSURE_AUTH_AUDIENCE', value: authAudience }
      { name: 'SEWSURE_AUTH_JWKS_URL', value: authJwksUrl }
      { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: monitoring.outputs.appInsightsConnectionString }
    ]
  }
}

module staticWebApp '../modules/staticwebapp.bicep' = {
  name: 'staticwebapp'
  params: {
    name: 'swa-${prefix}'
    location: staticWebAppLocation
    tags: tags
  }
}

module budget '../modules/budget.bicep' = {
  name: 'budget'
  params: {
    name: 'budget-${prefix}'
    amount: int(budgetAmount)
    contactEmails: budgetContactEmails
  }
}

// azd reads these as environment values after provisioning.
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = identity.outputs.tenantId
output AZURE_CLIENT_ID string = identity.outputs.clientId
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = registry.outputs.loginServer
output AZURE_CONTAINER_ENVIRONMENT_ID string = containerApps.outputs.environmentId
output API_URI string = 'https://${containerApps.outputs.apiFqdn}'
output API_JOB_NAME string = containerApps.outputs.jobName
output KEY_VAULT_URI string = keyVault.outputs.uri
output BLOB_ENDPOINT string = storage.outputs.blobEndpoint
output POSTGRES_HOST string = postgres.outputs.fqdn
output SITE_HOSTNAME string = staticWebApp.outputs.defaultHostname
