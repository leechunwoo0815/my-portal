/**
 * 知识库API - 独立模块
 */
import request from './client'

export const getKnowledgeBases = () =>
  request.get('/v1/knowledge/bases')

export const createKnowledgeBase = (data: any) =>
  request.post('/v1/knowledge/bases', data)

export const updateKnowledgeBase = (id: number, data: any) =>
  request.put(`/v1/knowledge/bases/${id}`, data)

export const deleteKnowledgeBase = (id: number) =>
  request.delete(`/v1/knowledge/bases/${id}`)

export const uploadDocument = (kbId: number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/v1/knowledge/bases/${kbId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getDocuments = (kbId: number) =>
  request.get(`/v1/knowledge/bases/${kbId}/documents`)

export const deleteDocument = (kbId: number, docId: number) =>
  request.delete(`/v1/knowledge/bases/${kbId}/documents/${docId}`)

export const queryKnowledgeBase = (kbId: number, data: { question: string; top_k?: number }) =>
  request.post(`/v1/knowledge/bases/${kbId}/query`, data)
