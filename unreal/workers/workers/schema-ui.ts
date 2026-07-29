import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaUiHandler: WorkerDefinition = {
  name: 'schema-ui',
  group: 'schema',
  description: 'Creates UE5 UMG widgets and UI layouts',
  keywords: ['ui', 'umg', 'widget', 'menu', 'hud', 'arayüz'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create_widget'
    const name = (params.name as string) || 'WBP_NewWidget'
    const type = (params.type as string) || 'menu'

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'create_widget' ? `
factory = unreal.WidgetBlueprintFactory()
factory.parent_class = unreal.UserWidget
widget = asset_tools.create_asset('${name}', '/Game/UI', None, factory)
` : action === 'add_button' ? `
widget = unreal.EditorAssetLibrary.load_asset('/Game/UI/${name}')
# add button via widget blueprint editor API
` : action === 'set_layout' ? `
widget = unreal.EditorAssetLibrary.load_asset('/Game/UI/${name}')
# set layout via widget blueprint
` : ''}
`

    return {
      success: true,
      output: `UI ${action}: ${name}`,
      data: { action, name, type, pythonScript: python },
    }
  },
}
