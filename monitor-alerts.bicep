// ============================================================
// monitor-alerts.bicep — Task 4 | CS2-IN-NCB | Knowledge Hub
// Deploys Azure Monitor diagnostic settings + alert rules
// for App Service and Azure SQL DB
// ============================================================

@description('Name of the existing Web App')
param webAppName string = 'app-monitoring-knowledgehub'

@description('Full resource ID of the Azure SQL Database')
param sqlDbResourceId string = '/subscriptions/${subscription().subscriptionId}/resourceGroups/rg-knowledgehub-spoke2/providers/Microsoft.Sql/servers/sql-knowledgehub-dev/databases/db-monitoring'

@description('Email address for alert notifications')
param alertEmail string = 'mvandijk@knowledgehub.local'

@description('Location')
param location string = 'spaincentral'

var tags = {
  Project:     'CS2-IN-NCB'
  Environment: 'Dev'
  Owner:       'mvandijk@knowledgehub.local'
  CostCenter:  'IT-Library'
}

// ── Log Analytics Workspace ───────────────────────────────────
resource logWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name:     'log-knowledgehub-monitoring'
  location: location
  tags:     tags
  properties: {
    sku: {
      name: 'PerGB2018'   // pay-per-GB, cheapest option
    }
    retentionInDays: 30
  }
}

// ── Reference existing Web App (same resource group) ─────────
resource webApp 'Microsoft.Web/sites@2023-01-01' existing = {
  name: webAppName
}

// ── Diagnostic Settings: App Service → Log Analytics ─────────
resource appServiceDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name:  'diag-appservice'
  scope: webApp
  properties: {
    workspaceId: logWorkspace.id
    logs: [
      {
        category: 'AppServiceHTTPLogs'
        enabled: true
      }
      {
        category: 'AppServiceConsoleLogs'
        enabled: true
      }
      {
        category: 'AppServiceAppLogs'
        enabled: true
      }
      {
        category: 'AppServiceAuditLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// ── Action Group (email notification) ────────────────────────
resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name:     'ag-knowledgehub-alerts'
  location: 'global'
  tags:     tags
  properties: {
    groupShortName: 'KHAlerts'
    enabled:        true
    emailReceivers: [
      {
        name:                 'IT-Admin'
        emailAddress:         alertEmail
        useCommonAlertSchema: true
      }
    ]
  }
}

// ── Alert Rule 1: SQL DB CPU > 80% ───────────────────────────
resource sqlCpuAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name:     'alert-sql-cpu-high'
  location: 'global'
  tags:     tags
  properties: {
    description:        'Azure SQL db-monitoring CPU usage exceeded 80%'
    severity:           2   // Warning
    enabled:            true
    scopes:             [sqlDbResourceId]
    evaluationFrequency: 'PT5M'
    windowSize:          'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name:            'CpuHigh'
          metricName:      'cpu_percent'
          metricNamespace: 'Microsoft.Sql/servers/databases'
          operator:        'GreaterThan'
          threshold:       80
          timeAggregation: 'Average'
          criterionType:   'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

// ── Alert Rule 2: App Service HTTP 5xx errors ─────────────────
resource appHttp5xxAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name:     'alert-appservice-5xx'
  location: 'global'
  tags:     tags
  properties: {
    description:        'Flask API returning HTTP 5xx errors'
    severity:           1   // Error
    enabled:            true
    scopes:             [webApp.id]
    evaluationFrequency: 'PT1M'
    windowSize:          'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name:            'Http5xx'
          metricName:      'Http5xx'
          metricNamespace: 'Microsoft.Web/sites'
          operator:        'GreaterThan'
          threshold:       5
          timeAggregation: 'Count'
          criterionType:   'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: actionGroup.id
      }
    ]
  }
}

output logWorkspaceId   string = logWorkspace.id
output actionGroupId    string = actionGroup.id
