/**
 * 项目状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getConfig, saveConfig as apiSaveConfig } from '@/api'

export const useProjectStore = defineStore('project', () => {
  // 状态
  const config = ref({
    region_name: '',
    survey_year: new Date().getFullYear(),
    historical_year: null,
    grading_standards: {}
  })

  const uploadedFile = ref(null)
  const dataPreview = ref([])
  const columns = ref([])
  const isLoading = ref(false)

  // 计算属性
  const hasData = computed(() => uploadedFile.value !== null)
  const isConfigured = computed(() => config.value.region_name !== '')

  // 方法
  const loadConfig = async () => {
    isLoading.value = true
    try {
      const data = await getConfig()
      config.value = data
    } catch (error) {
      console.error('加载配置失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const saveConfig = async () => {
    isLoading.value = true
    try {
      const data = await apiSaveConfig(config.value)
      config.value = data
    } catch (error) {
      console.error('保存配置失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const setUploadedFile = (file, preview, cols) => {
    uploadedFile.value = file
    dataPreview.value = preview
    columns.value = cols
  }

  const clearUploadedFile = () => {
    uploadedFile.value = null
    dataPreview.value = []
    columns.value = []
  }

  return {
    // 状态
    config,
    uploadedFile,
    dataPreview,
    columns,
    isLoading,
    // 计算属性
    hasData,
    isConfigured,
    // 方法
    loadConfig,
    saveConfig,
    setUploadedFile,
    clearUploadedFile
  }
})
