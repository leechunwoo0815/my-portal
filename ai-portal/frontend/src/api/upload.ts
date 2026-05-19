import request from '@/api/client'

export interface UploadResponse {
  url: string
  filename: string
}

export const uploadImage = (file: File, module: string) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('module', module)
  return request.post<UploadResponse>('/v1/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const uploadCover = (file: File, module: string, recordId: string) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('module', module)
  formData.append('record_id', recordId)
  return request.post<UploadResponse>('/v1/upload/cover', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
