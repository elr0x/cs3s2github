@description('SQL Server admin username')
param adminLogin string = 'sqladmin'

@secure()
@description('SQL Server admin password')
param adminPassword string

@description('Location for all resources')
param location string = 'spaincentral'

@description('Environment tag')
param environment string = 'Dev'

resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: 'sql-knowledgehub-dev'
  location: location
  tags: {
    Project: 'CS2-IN-NCB'
    Environment: environment
    Owner: 'mvandijk@knowledgehub.local'
    CostCenter: 'IT-Library'
    CreatedDate: '2026-04-10'
  }
  properties: {
    administratorLogin: adminLogin
    administratorLoginPassword: adminPassword
    publicNetworkAccess: 'Disabled'
    minimalTlsVersion: '1.2'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
  parent: sqlServer
  name: 'db-monitoring'
  location: location
  tags: {
    Project: 'CS2-IN-NCB'
    Environment: environment
    Owner: 'mvandijk@knowledgehub.local'
    CostCenter: 'IT-Library'
    CreatedDate: '2026-04-10'
  }
  sku: {
    name: 'GP_S_Gen5_1'
    tier: 'GeneralPurpose'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: 2147483648
    autoPauseDelay: 60
    minCapacity: json('0.5')
    requestedBackupStorageRedundancy: 'Local'
  }
}