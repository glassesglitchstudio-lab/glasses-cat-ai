import { WorkerDefinition, WorkerResult } from '../worker.types'

export const buildShaderHandler: WorkerDefinition = {
  name: 'build-shader',
  group: 'build',
  description: 'Compiles and validates UE5 shaders',
  keywords: ['shader', 'shader compile', 'material derle', 'gölgelendirici'],
  handler: async (params): Promise<WorkerResult> => {
    const action = (params.action as string) || 'compile_all'
    const platform = (params.platform as string) || 'Win64'
    const shaderModel = params.shader_model as number | undefined

    const cmd = [
      'RunUAT.bat BuildCookRun',
      `-platform=${platform}`,
      '-cook',
      '-ShaderCompile',
      `-ShaderCompileMethod=${action === 'compile_all' ? 'full' : action}`,
      ...(shaderModel ? [`-ShaderModel=${shaderModel}`] : []),
    ].join(' ')

    return { success: true, output: cmd, data: { action, platform, shaderModel } }
  },
}
