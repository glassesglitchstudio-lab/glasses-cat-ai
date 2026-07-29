import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaAnimationHandler: WorkerDefinition = {
  name: 'schema-animation',
  group: 'schema',
  description: 'Creates and manages UE5 animations and Animation Blueprints',
  keywords: ['animation', 'animasyon', 'anim', 'blend space', 'montage'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create_animation'
    const name = (params.name as string) || 'NewAnimation'
    const skeleton = (params.skeleton as string) || 'SKM_Character'

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'create_animation' ? `
skel = unreal.EditorAssetLibrary.load_asset('/Game/Characters/${skeleton}')
factory = unreal.AnimationFactory()
factory.target_skeleton = skel
asset_tools.create_asset('${name}', '/Game/Animations', None, factory)
` : action === 'create_anim_bp' ? `
skel = unreal.EditorAssetLibrary.load_asset('/Game/Characters/${skeleton}')
factory = unreal.BlueprintFactory()
factory.parent_class = unreal.AnimBlueprint
factory.target_skeleton = skel
asset_tools.create_asset('${name}', '/Game/Animations', None, factory)
` : ''}
`

    return {
      success: true,
      output: `Animation ${action}: ${name}`,
      data: { action, name, skeleton, pythonScript: python },
    }
  },
}
