import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaVfxHandler: WorkerDefinition = {
  name: 'schema-vfx',
  group: 'schema',
  description: 'Creates UE5 Niagara VFX systems and emitters',
  keywords: ['vfx', 'niagara', 'efekt', 'particle', 'patlama'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create_niagara'
    const name = (params.name as string) || 'NS_NewEffect'
    const type = (params.type as string) || 'explosion'

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'create_niagara' ? `
factory = unreal.NiagaraScriptFactory()
factory.usage = unreal.NiagaraScriptUsage.SYSTEM_SPAWN_SCRIPT
niagara_sys = asset_tools.create_asset('${name}', '/Game/VFX', None, factory)
` : action === 'particle_settings' ? `
niagara_sys = unreal.EditorAssetLibrary.load_asset('/Game/VFX/${name}')
emitter_handle = niagara_sys.get_emitter_handle(0)
emitter_handle.set_sim_target(unreal.NiagaraSimTarget.GPUComputeSim)
` : ''}
`

    return {
      success: true,
      output: `VFX ${action}: ${name}`,
      data: { action, name, type, pythonScript: python },
    }
  },
}
