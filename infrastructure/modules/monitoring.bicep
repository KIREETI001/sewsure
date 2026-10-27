// Log Analytics workspace + workspace-based Application Insights.
param logAnalyticsName string
param appInsightsName string
param location string
param tags object = {}
@minValue(30)
@maxValue(730)
param retentionInDays int = 30
@description('Daily ingestion cap in GB. Protects the student-credit budget; -1 disables the cap.')
param dailyQuotaGb int = 1

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionInDays
    workspaceCapping: {
      dailyQuotaGb: dailyQuotaGb
    }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
  }
}

output logAnalyticsId string = logAnalytics.id
output logAnalyticsName string = logAnalytics.name
output appInsightsId string = appInsights.id
output appInsightsName string = appInsights.name
// Resolved at deploy time and never written to the repo.
output appInsightsConnectionString string = appInsights.properties.ConnectionString
