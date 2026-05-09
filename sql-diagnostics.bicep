// ============================================================
// sql-diagnostics.bicep — Module for cross-RG SQL diagnostics
// Deployed into rg-knowledgehub-spoke2 where the SQL DB lives
// ============================================================

@description('Name of the Azure SQL Server')
param sqlServerName string

@description('Name of the Azure SQL Database')
param sqlDbName string

@description('Log Analytics Workspace ID to send logs to')
param workspaceId string

// ── Reference existing SQL DB in this resource group ─────────
resource sqlDb 'Microsoft.Sql/servers/databases@2022-05-01-preview' existing = {
  name: '${sqlServerName}/${sqlDbName}'
}

// ── Diagnostic Settings: Azure SQL → Log Analytics ───────────
resource sqlDiag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name:  'diag-sql'
  scope: sqlDb
  properties: {
    workspaceId: workspaceId
    logs: [
      {
        category: 'SQLInsights'
        enabled: true
      }
      {
        category: 'Errors'
        enabled: true
      }
      {
        category: 'Timeouts'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'Basic'
        enabled: true
      }
    ]
  }
}
