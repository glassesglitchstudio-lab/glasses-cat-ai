import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaAiHandler: WorkerDefinition = {
  name: 'schema-ai',
  group: 'schema',
  description: 'Creates UE5 AI behavior trees, blackboards, and EQS',
  keywords: ['ai', 'yapay zeka', 'behavior', 'davranış', 'blackboard', 'eqs'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create_behavior_tree'
    const name = (params.name as string) || 'BT_NewAI'
    const type = (params.type as string) || 'enemy'

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'create_behavior_tree' ? `
factory = unreal.BehaviorTreeFactory()
bt = asset_tools.create_asset('${name}', '/Game/AI', None, factory)
bb_factory = unreal.BlackboardFactory()
bb = asset_tools.create_asset('${name}_BB', '/Game/AI', None, bb_factory)
bt.blackboard_asset = bb
` : action === 'create_eqs' ? `
factory = unreal.EnvironmentQueryFactory()
eqs = asset_tools.create_asset('${name}', '/Game/AI', None, factory)
` : action === 'create_controller' ? `
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.AIController
asset_tools.create_asset('${name}', '/Game/AI', None, factory)
` : ''}
`

    return {
      success: true,
      output: `AI ${action}: ${name}`,
      data: { action, name, type, pythonScript: python },
    }
  },
}
