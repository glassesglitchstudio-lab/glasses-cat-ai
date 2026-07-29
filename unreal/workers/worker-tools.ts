import { WORKERS } from './index'

export function registerWorkerTools(plugin: any) {
  for (const worker of WORKERS) {
    plugin.registerTool({
      name: `ue5_${worker.name}`,
      description: worker.description,
      handler: async (params: Record<string, unknown>) => {
        return worker.handler(params)
      },
      schema: {
        type: 'object',
        properties: {},
      },
    })
  }
}
