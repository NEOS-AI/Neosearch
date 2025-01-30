import { anthropic } from '@ai-sdk/anthropic'
import { createAzure } from '@ai-sdk/azure'
import { deepseek } from '@ai-sdk/deepseek'
import { google } from '@ai-sdk/google'
import { createOpenAI, openai } from '@ai-sdk/openai'
import { experimental_createProviderRegistry as createProviderRegistry } from 'ai'
import { createOllama } from 'ollama-ai-provider'

export const registry = createProviderRegistry({
  openai,
  anthropic,
  google,
  groq: createOpenAI({
    apiKey: process.env.GROQ_API_KEY,
    baseURL: 'https://api.groq.com/openai/v1'
  }),
  ollama: createOllama({
    baseURL: `${process.env.OLLAMA_BASE_URL}/api`
  }),
  azure: createAzure({
    apiKey: process.env.AZURE_API_KEY,
    resourceName: process.env.AZURE_RESOURCE_NAME
  }),
  deepseek,
  'openai-compatible': createOpenAI({
    apiKey: process.env.OPENAI_COMPATIBLE_API_KEY,
    baseURL: process.env.OPENAI_COMPATIBLE_API_BASE_URL
  })
})

export function getModel(model: string) {
  // if ollama provider, set simulateStreaming to true
  if (model.includes('ollama')) {
    const modelName = model.split(':')[1]
    const ollama = createOllama({
      baseURL: `${process.env.OLLAMA_BASE_URL}/api`
    })
    return ollama(modelName, {
      simulateStreaming: true
    })
  }

  return registry.languageModel(model)
}

export function isProviderEnabled(providerId: string): boolean {
  switch (providerId) {
    case 'openai':
      return !!process.env.OPENAI_API_KEY
    case 'anthropic':
      return !!process.env.ANTHROPIC_API_KEY
    case 'google':
      return !!process.env.GOOGLE_GENERATIVE_AI_API_KEY
    case 'groq':
      return !!process.env.GROQ_API_KEY
    case 'ollama':
      return !!process.env.OLLAMA_BASE_URL
    case 'azure':
      return !!process.env.AZURE_API_KEY && !!process.env.AZURE_RESOURCE_NAME
    case 'deepseek':
      return !!process.env.DEEPSEEK_API_KEY
    case 'openai-compatible':
      return (
        !!process.env.OPENAI_COMPATIBLE_API_KEY &&
        !!process.env.OPENAI_COMPATIBLE_API_BASE_URL &&
        !!process.env.NEXT_PUBLIC_OPENAI_COMPATIBLE_MODEL
      )
    default:
      return false
  }
}
