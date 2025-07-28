import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiService from '@/services/api'

export const useAppStore = defineStore('app', () => {
  // 状态
  const config = ref(null)
  const health = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const isConfigLoaded = computed(() => config.value !== null)
  const isHealthy = computed(() => health.value?.status === 'healthy')

  // 动作
  const loadConfig = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await apiService.getConfig()
      config.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkHealth = async () => {
    try {
      const response = await apiService.checkHealth()
      health.value = response.data
      return response.data.status
    } catch (err) {
      health.value = { status: 'unhealthy', message: err.message }
      return 'unhealthy'
    }
  }

  const translateText = async (text, targetLanguage = null) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiService.translateText({ 
        text, 
        target_language: targetLanguage 
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const translateFile = async (file, maxConcurrent = 5) => {
    loading.value = true
    error.value = null
    try {
      const response = await apiService.translateFile(file, maxConcurrent)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const listFiles = async () => {
    try {
      const response = await apiService.listFiles()
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const downloadFile = (filename) => {
    return apiService.downloadFile(filename)
  }

  return {
    // 状态
    config,
    health,
    loading,
    error,
    
    // 计算属性
    isConfigLoaded,
    isHealthy,
    
    // 动作
    loadConfig,
    checkHealth,
    translateText,
    translateFile,
    listFiles,
    downloadFile
  }
})