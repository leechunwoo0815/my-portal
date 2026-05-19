import { ElMessage } from 'element-plus'
import { uploadImage } from '@/api/upload'

export function useMdEditorUpload(module: string) {
  const handleUploadImage = async (_event: any, _insertImage: Function, files: FileList) => {
    const file = files[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请选择图片文件')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过10MB')
      return
    }
    try {
      const res: any = await uploadImage(file, module)
      _insertImage({ url: res.url, desc: file.name })
    } catch (e: any) {
      ElMessage.error(e?.message || '图片上传失败')
    }
  }
  return { handleUploadImage }
}
