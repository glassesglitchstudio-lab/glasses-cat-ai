import { WorkerDefinition, WorkerResult } from '../worker.types'

export const buildPackageHandler: WorkerDefinition = {
  name: 'build-package',
  group: 'build',
  description: 'Packages UE5 project for distribution',
  keywords: ['package', 'paketle', 'build çıkar', 'archive'],
  handler: async (params): Promise<WorkerResult> => {
    const platform = (params.platform as string) || 'Win64'
    const configuration = (params.configuration as string) || 'Shipping'
    const project = (params.project as string) || 'current'
    const archive = params.archive as boolean | undefined
    const demo = params.demo as boolean | undefined
    const debugSymbols = params.debug_symbols as boolean | undefined

    const cmd = [
      'RunUAT.bat BuildCookRun',
      `-project=${project}`,
      `-platform=${platform}`,
      `-target=${configuration}`,
      '-build',
      '-stage',
      '-pak',
      ...(archive ? ['-archive'] : []),
      ...(demo ? ['-demo'] : []),
      ...(debugSymbols ? ['-DebugSymbols'] : []),
    ].join(' ')

    return { success: true, output: cmd, data: { command: cmd } }
  },
}
