import { WorkerDefinition, WorkerResult, ToolCall } from './worker.types'
import { buildCookHandler } from './workers/build-cook'
import { buildPackageHandler } from './workers/build-package'
import { buildShaderHandler } from './workers/build-shader'
import { buildAssetHandler } from './workers/build-asset'
import { buildOptimizeHandler } from './workers/build-optimize'
import { schemaLevelHandler } from './workers/schema-level'
import { schemaBlueprintHandler } from './workers/schema-blueprint'
import { schemaMaterialHandler } from './workers/schema-material'
import { schemaAnimationHandler } from './workers/schema-animation'
import { schemaVfxHandler } from './workers/schema-vfx'
import { schemaAudioHandler } from './workers/schema-audio'
import { schemaUiHandler } from './workers/schema-ui'
import { schemaAiHandler } from './workers/schema-ai'

const WORKERS: WorkerDefinition[] = [
  buildCookHandler,
  buildPackageHandler,
  buildShaderHandler,
  buildAssetHandler,
  buildOptimizeHandler,
  schemaLevelHandler,
  schemaBlueprintHandler,
  schemaMaterialHandler,
  schemaAnimationHandler,
  schemaVfxHandler,
  schemaAudioHandler,
  schemaUiHandler,
  schemaAiHandler,
]

const WORKER_MAP = new Map(WORKERS.map(w => [w.name, w]))

export function getWorker(name: string): WorkerDefinition | undefined {
  return WORKER_MAP.get(name)
}

export function routeToWorker(text: string): WorkerDefinition | undefined {
  const lower = text.toLowerCase()
  for (const worker of WORKERS) {
    for (const kw of worker.keywords) {
      if (lower.includes(kw)) return worker
    }
  }
  return undefined
}

export async function executeToolCall(toolCall: ToolCall): Promise<WorkerResult> {
  const worker = getWorker(toolCall.worker)
  if (!worker) return { success: false, error: `Worker not found: ${toolCall.worker}` }
  return worker.handler(toolCall.params)
}

export { WORKERS, WORKER_MAP }
