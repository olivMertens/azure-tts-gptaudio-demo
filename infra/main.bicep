@minLength(1)
@description('Primary location for all resources')
param location string = 'swedencentral'

@description('Name of the resource group to deploy to.')
param rootname string = 'azure-tts-gptaudio-demo'

param openAIName string = '${rootname}-${location}-${uniqueString(resourceGroup().id)}'

@description('Model deployments for OpenAI')
param deployments array = [
  {
    name: 'gpt-audio'
    model: 'gpt-audio'
    capacity: 1000
    version: '2025-08-28'
    deployment: 'GlobalStandard'
  }
  {
    name: 'gpt-5-nano'
    model: 'gpt-5-nano'
    capacity: 1000
    version: '2025-08-07'
    deployment: 'GlobalStandard'
  }
]

@description('Creates an Azure OpenAI resource.')
resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAIName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAIName
    publicNetworkAccess: 'Enabled'
    restore: false
  }
}

@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [
  for deployment in deployments: {
    parent: openAI
    name: deployment.name
    sku: {
      name: deployment.deployment
      capacity: deployment.capacity
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: deployment.name
        version: deployment.version
      }
    }
  }
]

output AZURE_OPENAI_ENDPOINT string = openAI.properties.endpoint
output AZURE_OPENAI_API_KEY string = listKeys(openAI.id, openAI.apiVersion).key1
output AZURE_OPENAI_API_VERSION string = '2025-01-01-preview'
output AZURE_OPENAI_DEPLOYMENT_NAME string = deployments[0].name
output AZURE_OPENAI_NANO_DEPLOYMENT_NAME string = 'gpt-5-nano'

output AZURE_OPENAI_TEXT_ENDPOINT string = 'https://your-text-resource.cognitiveservices.azure.com/'
output AZURE_OPENAI_TEXT_API_KEY string = 'your_text_api_key_here'
output AZURE_OPENAI_TEXT_DEPLOYMENT_NAME string = 'your-gpt-text-deployment-name'
output AZURE_OPENAI_TEXT_API_VERSION string = '2024-12-01-preview'
