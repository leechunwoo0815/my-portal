import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { getModels } from '@/api/chat'

export interface ModelInfo {
  id: string
  name: string
  provider: string
  description: string
}

export const useModelsStore = defineStore('models', () => {
  const models = ref<ModelInfo[]>([])
  const currentModel = ref<string>(localStorage.getItem('chat_model') || '')

  watch(currentModel, (val) => localStorage.setItem('chat_model', val))

  const fetchModels = async () => {
    try {
      models.value = await getModels() as any
      if (models.value.length > 0 && !currentModel.value) {
        currentModel.value = models.value[0].id
      }
    } catch (e) {
      (window as any).__LOG?.('error', '获取模型列表失败', e)
    }
  }

  return { models, currentModel, fetchModels }
})
