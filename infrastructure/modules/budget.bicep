// Resource-group budget with actual and forecast alerts (deploy at resource group scope).
param name string
@description('Monthly budget in the billing currency of the subscription.')
param amount int
param contactEmails array
@description('First day of the budget month. Defaults to the first of the current month at deploy time.')
param startDate string = utcNow('yyyy-MM-01')
@description('Percent-of-budget thresholds for actual-cost alerts.')
param actualThresholds array = [
  50
  80
  100
]
param forecastThreshold int = 100

var actualNotifications = toObject(actualThresholds, t => 'actual${t}', t => {
  enabled: true
  operator: 'GreaterThanOrEqualTo'
  threshold: t
  thresholdType: 'Actual'
  contactEmails: contactEmails
})

var forecastNotifications = {
  forecast: {
    enabled: true
    operator: 'GreaterThanOrEqualTo'
    threshold: forecastThreshold
    thresholdType: 'Forecasted'
    contactEmails: contactEmails
  }
}

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: name
  properties: {
    category: 'Cost'
    amount: amount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: startDate
    }
    notifications: union(actualNotifications, forecastNotifications)
  }
}

output id string = budget.id
