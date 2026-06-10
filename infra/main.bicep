targetScope = 'subscription'

type OpenAiDeployment = {
  deploymentName: string
  modelName: string
  modelVersion: string
  capacity: int
  format: string?
  skuName: string?
}

type ClaudeModelDeployment = {
  name: string
  capacity: int
  version: string?
}

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Location for the OpenAI resource')
// Regions must support both the model AND the Responses API:
// Models by region: https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure?tabs=global-standard-aoai%2Cglobal-standard&pivots=azure-openai#models-by-deployment-type
// Responses API regions: https://learn.microsoft.com/azure/foundry/openai/how-to/responses?tabs=python-key#region-availability
@allowed([
  'australiaeast'
  'brazilsouth'
  'canadacentral'
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'germanywestcentral'
  'italynorth'
  'japaneast'
  'koreacentral'
  'northcentralus'
  'norwayeast'
  'polandcentral'
  'southafricanorth'
  'southcentralus'
  'southeastasia'
  'southindia'
  'spaincentral'
  'swedencentral'
  'switzerlandnorth'
  'uaenorth'
  'uksouth'
  'westus'
  'westus3'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

@description('List of OpenAI deployments to create in the OpenAI account.')
param azureOpenaiModels OpenAiDeployment[]

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Whether to assign Foundry roles to principalId.')
param assignRbac bool = false

@description('List of Claude model deployments to create in Foundry.')
param claudeModels ClaudeModelDeployment[]

@description('Organization name surfaced via Claude modelProviderData.')
param claudeOrganizationName string

@description('Two-letter ISO country code for Claude modelProviderData.')
@minLength(2)
@maxLength(2)
param claudeCountryCode string = 'US'

@description('Industry for Claude modelProviderData. Must be lowercase.')
@allowed([
  'technology'
  'finance'
  'healthcare'
  'education'
  'retail'
  'manufacturing'
  'government'
  'media'
  'other'
])
param claudeIndustry string = 'technology'

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var prefix = '${environmentName}${resourceToken}'
var tags = { 'azd-env-name': environmentName }
var baseName = 'claude'
var foundrySuffix = take(uniqueString(subscription().id, environmentName), 8)
var foundryAccountName = '${baseName}-foundry-${foundrySuffix}'
var foundryProjectName = '${baseName}-proj-${foundrySuffix}'

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
    name: '${prefix}-rg'
    location: location
    tags: tags
}

module foundry 'foundry.bicep' = {
  name: 'foundry'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    accountName: foundryAccountName
    projectName: foundryProjectName
    suffix: foundrySuffix
    openAiModels: azureOpenaiModels
    claudeModels: claudeModels
    claudeOrganizationName: claudeOrganizationName
    claudeCountryCode: claudeCountryCode
    claudeIndustry: claudeIndustry
    principalId: principalId
    assignRbac: assignRbac
  }
}

// Log Analytics workspace for Application Insights
var logAnalyticsName = '${prefix}-loganalytics'
module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.9.1' = {
  name: 'loganalytics'
  scope: resourceGroup
  params: {
    name: logAnalyticsName
    location: location
    tags: tags
  }
}

// Application Insights for OpenTelemetry export
var appInsightsName = '${prefix}-appinsights'
module appInsights 'br/public:avm/res/insights/component:0.4.2' = {
  name: 'appinsights'
  scope: resourceGroup
  params: {
    name: appInsightsName
    location: location
    tags: tags
    workspaceResourceId: logAnalytics.outputs.resourceId
    kind: 'web'
    applicationType: 'web'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

// Specific to Azure OpenAI
output AZURE_OPENAI_ENDPOINT string = foundry.outputs.openAiEndpoint
output AZURE_OPENAI_DEPLOYMENT_NAMES array = foundry.outputs.openAiDeploymentNames

// Specific to Application Insights
output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString

// Specific to Microsoft Foundry + Claude
output CLAUDE_BASE_URL string = foundry.outputs.claudeBaseUrl
output FOUNDRY_PROJECT_ENDPOINT string = foundry.outputs.foundryProjectEndpoint
output FOUNDRY_ACCOUNT_NAME string = foundry.outputs.foundryAccountName
output CLAUDE_DEPLOYMENT_NAMES array = foundry.outputs.claudeDeploymentNames
