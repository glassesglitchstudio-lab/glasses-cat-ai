import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaMaterialHandler: WorkerDefinition = {
  name: 'schema-material',
  group: 'schema',
  description: 'Creates and edits UE5 Materials and Material Instances',
  keywords: ['material', 'malzeme', 'shader', 'doku', 'texture'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create'
    const name = (params.name as string) || 'M_NewMaterial'
    const type = (params.type as string) || 'surface'

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'create' ? `
factory = unreal.MaterialFactoryNew()
mat = asset_tools.create_asset('${name}', '/Game/Materials', None, factory)
if '${type}' == 'surface':
    mat.blend_mode = unreal.BlendMode.BLEND_OPAQUE
elif '${type}' == 'translucent':
    mat.blend_mode = unreal.BlendMode.BLEND_TRANSLUCENT
` : action === 'add_parameter' ? `
mat = unreal.EditorAssetLibrary.load_asset('/Game/Materials/${name}')
param = unreal.MaterialEditingLibrary.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D)
param.parameter_name = '${(params.parameter_name as string) || 'NewParam'}'
` : ''}
`

    return {
      success: true,
      output: `Material ${action}: ${name}`,
      data: { action, name, type, pythonScript: python },
    }
  },
}
