import { WorkerDefinition, WorkerResult } from '../worker.types'

export const buildCookHandler: WorkerDefinition = {
  name: 'build-cook',
  group: 'build',
  description: 'Cooks content for UE5 builds using UAT BuildCookRun',
  keywords: ['cook', 'cook et', 'content build', 'paketle'],
  handler: async (params): Promise<WorkerResult> => {
    const target = (params.target as string) || 'Development'
    const platform = (params.platform as string) || 'Win64'
    const project = (params.project as string) || 'current'
    const maps = params.maps as string[] | undefined
    const iterative = params.iterative as boolean | undefined
    const clean = params.clean as boolean | undefined
    const compress = params.compress as boolean | undefined
    const validate = params.validate as boolean | undefined

    const cmd = [
      'RunUAT.bat BuildCookRun',
      `-project=${project}`,
      `-platform=${platform}`,
      `-target=${target}`,
      '-cook',
      '-build',
      ...(maps ? [`-map=${maps.join('+')}`] : []),
      ...(iterative ? ['-iterativecooking'] : []),
      ...(clean ? ['-clean'] : []),
      ...(compress ? ['-compressed'] : []),
      ...(validate ? ['-Validate'] : []),
    ].join(' ')

    return { success: true, output: cmd, data: { command: cmd } }
  },
}
