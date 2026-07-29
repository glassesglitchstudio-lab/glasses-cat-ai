import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaBlueprintHandler: WorkerDefinition = {
  name: 'schema-blueprint',
  group: 'schema',
  description: 'Creates and edits UE5 Blueprint classes',
  keywords: ['blueprint', 'bp', 'mavi', 'class'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create'
    const name = (params.name as string) || 'BP_NewClass'
    const parent = (params.parent as string) || 'Actor'

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'create' ? `
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.find_class('${parent}')
asset_tools.create_asset('${name}', '/Game/Blueprints', None, factory)
` : action === 'add_variable' ? `
bp = unreal.EditorAssetLibrary.load_blueprint_class('/Game/Blueprints/${name}')
# add variable via blueprint editor
` : ''}
`

    return {
      success: true,
      output: `Blueprint ${action}: ${name}`,
      data: { action, name, parent, pythonScript: python },
    }
  },
}
