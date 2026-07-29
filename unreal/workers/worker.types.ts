export interface WorkerDefinition {
  name: string
  group: 'build' | 'schema'
  description: string
  keywords: string[]
  handler: (params: Record<string, unknown>) => Promise<WorkerResult>
}

export interface WorkerResult {
  success: boolean
  output?: string
  error?: string
  data?: Record<string, unknown>
}

export interface ToolCall {
  worker: string
  params: Record<string, unknown>
}
