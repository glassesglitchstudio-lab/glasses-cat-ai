import { WorkerDefinition, WorkerResult } from '../worker.types'

export const schemaAudioHandler: WorkerDefinition = {
  name: 'schema-audio',
  group: 'schema',
  description: 'Creates and manages UE5 audio assets',
  keywords: ['audio', 'ses', 'sound', 'cue', 'metasound'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'import_sound'
    const name = (params.name as string) || 'S_NewSound'
    const file = (params.file as string) || ''

    const python = `
import unreal
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
${action === 'import_sound' ? `
import_task = unreal.AssetImportTask()
import_task.filename = '${file}'
import_task.destination_path = '/Game/Audio'
import_task.replace_existing = True
asset_tools.import_asset_tasks([import_task])
` : action === 'create_sound_cue' ? `
factory = unreal.SoundCueFactoryNew()
cue = asset_tools.create_asset('${name}', '/Game/Audio', None, factory)
` : action === 'create_metasound' ? `
factory = unreal.MetaSoundFactoryNew()
meta = asset_tools.create_asset('${name}', '/Game/Audio', None, factory)
` : ''}
`

    return {
      success: true,
      output: `Audio ${action}: ${name}`,
      data: { action, name, file, pythonScript: python },
    }
  },
}
