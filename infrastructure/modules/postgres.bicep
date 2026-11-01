// PostgreSQL Flexible Server, smallest burstable SKU. Microsoft Entra auth only:
// the managed identity is the administrator, so there is no password to store.
param name string
param location string
param tags object = {}
param tenantId string = tenant().tenantId
param skuName string = 'Standard_B1ms'
param skuTier string = 'Burstable'
@allowed([
  '15'
  '16'
])
param version string = '16'
@minValue(32)
param storageSizeGB int = 32
param databaseName string = 'sewsure'
@description('Managed identity that administers the server and is used by the API and Job.')
param adminIdentityPrincipalId string
param adminIdentityName string

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuTier
  }
  properties: {
    version: version
    storage: {
      storageSizeGB: storageSizeGB
      autoGrow: 'Disabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    authConfig: {
      activeDirectoryAuth: 'Enabled'
      passwordAuth: 'Disabled'
      tenantId: tenantId
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: server
  name: databaseName
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

resource entraAdmin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = {
  parent: server
  name: adminIdentityPrincipalId
  properties: {
    principalType: 'ServicePrincipal'
    principalName: adminIdentityName
    tenantId: tenantId
  }
  dependsOn: [
    database
  ]
}

// 0.0.0.0 - 0.0.0.0 means "Azure services" (Container Apps egress). Staging only;
// replace with VNet integration or a private endpoint before any real-user pilot.
resource allowAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: server
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
  dependsOn: [
    entraAdmin
  ]
}

output id string = server.id
output name string = server.name
output fqdn string = server.properties.fullyQualifiedDomainName
output databaseName string = database.name
