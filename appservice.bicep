// ============================================================
// appservice.bicep — Task 4 | CS2-IN-NCB | Knowledge Hub
// Deploys: App Service Plan + Web App (Flask API)
//          + Private Endpoint + Private DNS Zone
// REQ-S2P2-03: No public internet access
// REQ-S2P2-05: Monitoring API hosted on PaaS
// ============================================================

// ── Parameters ──────────────────────────────────────────────
@description('Azure region for all resources')
param location string = 'spaincentral'

@description('App Service Plan name')
param appServicePlanName string = 'asp-knowledgehub-api'

@description('Web App name — must be globally unique')
param webAppName string = 'app-knowledgehub-api'

@description('Python runtime version')
param pythonVersion string = 'PYTHON|3.11'

@description('Spoke 1 VNet resource ID (for Private Endpoint)')
param spoke1VnetId string

@description('App Subnet resource ID inside Spoke 1 (10.1.1.0/24)')
param appSubnetId string

@description('Azure SQL connection string (from Key Vault reference or param)')
@secure()
param dbConnectionString string

@description('API Key for Flask authentication')
@secure()
param apiKey string

@description('Hub VNet resource ID (for DNS Zone link)')
param hubVnetId string

// ── Variables ────────────────────────────────────────────────
var privateEndpointName   = 'pe-${webAppName}'
var privateNicName        = 'pe-${webAppName}-nic'
var privateDnsZoneName    = 'privatelink.azurewebsites.net'
var dnsZoneLinkNameSpoke1 = 'link-spoke1-appservice'
var dnsZoneLinkNameHub    = 'link-hub-appservice'
var tags = {
  Project:     'CS2-IN-NCB'
  Environment: 'Dev'
  Owner:       'mvandijk@knowledgehub.local'
  CostCenter:  'IT-Library'
  CreatedDate: '2026-04-15'
}

// ── App Service Plan (Linux B1 — cheapest paid tier) ────────
// B1 supports VNet integration; Free F1 does NOT → can't use Private Endpoint
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name:     appServicePlanName
  location: location
  tags:     tags
  sku: {
    name:     'B1'
    tier:     'Basic'
    size:     'B1'
    family:   'B'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true   // required for Linux
  }
}

// ── Web App (Flask API) ──────────────────────────────────────
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name:     webAppName
  location: location
  tags:     tags
  kind:     'app,linux'
  identity: {
    type: 'SystemAssigned'   // for future Key Vault access
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly:    true        // REQ-S2P2-03: HTTPS only

    siteConfig: {
      linuxFxVersion:        pythonVersion
      alwaysOn:              false         // Dev: save cost
      ftpsState:             'Disabled'    // Security hardening
      minTlsVersion:         '1.2'
      http20Enabled:         true
      publicNetworkAccess:   'Disabled'    // REQ-S2P2-03: NO public access

      // ── Application Settings (env vars for Flask) ──────────
      appSettings: [
        {
          name:  'FLASK_ENV'
          value: 'production'
        }
        {
          name:  'FLASK_HOST'
          value: '0.0.0.0'
        }
        {
          name:  'FLASK_PORT'
          value: '8000'
        }
        {
          name:  'API_KEY'            // Flask API Key auth — REQ-S2P2-05
          value: apiKey
        }
        {
          name:  'DB_CONNECTION_STRING'  // Azure SQL — REQ-S2P2-04
          value: dbConnectionString
        }
        {
          name:  'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'              // pip install on deploy
        }
        {
          name:  'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]

      // ── Startup command for Flask ───────────────────────────
      appCommandLine: 'gunicorn --bind 0.0.0.0:8000 --workers 2 app:app'
    }
  }
}

// ── Private Endpoint (REQ-S2P2-03) ──────────────────────────
// Connects webApp exclusively to Spoke1 AppSubnet — no public internet
resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-05-01' = {
  name:     privateEndpointName
  location: location
  tags:     tags
  properties: {
    subnet: {
      id: appSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: privateEndpointName
        properties: {
          privateLinkServiceId: webApp.id
          groupIds: ['sites']     // 'sites' = App Service target sub-resource
        }
      }
    ]
    customNetworkInterfaceName: privateNicName
  }
}

// ── Private DNS Zone (privatelink.azurewebsites.net) ─────────
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name:     privateDnsZoneName
  location: 'global'            // DNS zones are always global
  tags:     tags
}

// ── DNS Zone Link → Spoke1 VNet ──────────────────────────────
resource dnsZoneLinkSpoke1 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent:   privateDnsZone
  name:     dnsZoneLinkNameSpoke1
  location: 'global'
  properties: {
    virtualNetwork: {
      id: spoke1VnetId
    }
    registrationEnabled: false
  }
}

// ── DNS Zone Link → Hub VNet (so on-prem DNS resolver can resolve) ──
resource dnsZoneLinkHub 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent:   privateDnsZone
  name:     dnsZoneLinkNameHub
  location: 'global'
  properties: {
    virtualNetwork: {
      id: hubVnetId
    }
    registrationEnabled: false
  }
}

// ── DNS Zone Group (auto-creates A record for Private Endpoint IP) ──
resource dnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-05-01' = {
  parent: privateEndpoint
  name:   'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-azurewebsites-net'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
  }
}

// ── Outputs ──────────────────────────────────────────────────
output webAppName       string = webApp.name
output webAppHostname   string = webApp.properties.defaultHostName
output privateEndpointIp string = '(see Private Endpoint NIC after deployment)'
output principalId      string = webApp.identity.principalId
output appServicePlanId string = appServicePlan.id
