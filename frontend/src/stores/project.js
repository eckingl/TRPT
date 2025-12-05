/**
 * 项目状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getConfig, saveConfig as apiSaveConfig } from '@/api'

export const useProjectStore = defineStore('project', () => {
  // ============ 选择状态（跨页面保持）============
  const selectedCategory = ref(null)
  const selectedTopic = ref(null)
  const selectedRegion = ref(null)

  // ============ 项目配置 ============
  const config = ref({
    region_name: '',
    survey_year: new Date().getFullYear(),
    historical_year: null,
    grading_standards: {}
  })

  // ============ 数据状态 ============
  const uploadedFile = ref(null)
  const dataPreview = ref([])
  const columns = ref([])
  const isLoading = ref(false)

  // ============ 计算属性 ============
  const hasData = computed(() => uploadedFile.value !== null)
  const isConfigured = computed(() => config.value.region_name !== '')
  const hasSelection = computed(() =>
    selectedCategory.value && selectedTopic.value && selectedRegion.value
  )

  // ============ 选择方法 ============
  const setSelection = (category, topic, region) => {
    selectedCategory.value = category
    selectedTopic.value = topic
    selectedRegion.value = region
    // 同步到 config
    if (region) {
      config.value.regionId = region.id
      config.value.regionName = region.name
    }
  }

  const clearSelection = () => {
    selectedCategory.value = null
    selectedTopic.value = null
    selectedRegion.value = null
  }

  // ============ 配置方法 ============
  const loadConfig = async () => {
    isLoading.value = true
    try {
      const data = await getConfig()
      config.value = { ...config.value, ...data }
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
      config.value = { ...config.value, ...data }
    } catch (error) {
      console.error('保存配置失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // ============ 数据方法 ============
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
    // 选择状态
    selectedCategory,
    selectedTopic,
    selectedRegion,
    // 配置状态
    config,
    uploadedFile,
    dataPreview,
    columns,
    isLoading,
    // 计算属性
    hasData,
    isConfigured,
    hasSelection,
    // 选择方法
    setSelection,
    clearSelection,
    // 配置方法
    loadConfig,
    saveConfig,
    // 数据方法
    setUploadedFile,
    clearUploadedFile
  }
})
