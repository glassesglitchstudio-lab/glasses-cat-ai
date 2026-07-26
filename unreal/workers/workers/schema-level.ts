import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaLevelHandler: WorkerDefinition = {
  name: 'schema-level',
  group: 'schema',
  description: 'Creates and manages UE5 levels/worlds',
  keywords: ['level', 'seviye', 'world', 'world composition', 'streaming level'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'create'
    const name = (params.name as string) || 'NewLevel'
    const template = (params.template as string) || 'empty'

    const python = `
import unreal
level_lib = unreal.EditorLevelLibrary()
${action === 'create' ? `
level_lib.new_level('/Game/${name}')
` : action === 'lighting_setup' ? `
subsystem = unreal.get_editor_subsystem(unreal.LightmassSubsystem)
subsystem.build_lighting()
` : ''}
`

    return {
      success: true,
      output: `Level ${action}: ${name}`,
      data: { action, name, template, pythonScript: python },
    }
  },
}
