// Static Web App for the informational site + waitlist (apps/site).
// Free tier. Content deploys via azd / the staging workflow, not via a repo link.
param name string
@description('Static Web Apps are available in a limited set of regions.')
@allowed([
  'westus2'
  'centralus'
  'eastus2'
  'westeurope'
  'eastasia'
])
param location string = 'eastasia'
param tags object = {}

resource site 'Microsoft.Web/staticSites@2023-12-01' = {
  name: name
  location: location
  tags: union(tags, {
    'azd-service-name': 'site'
  })
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    stagingEnvironmentPolicy: 'Enabled'
    allowConfigFileUpdates: true
  }
}

output id string = site.id
output name string = site.name
output defaultHostname string = site.properties.defaultHostname
