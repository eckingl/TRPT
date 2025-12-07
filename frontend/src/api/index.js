/**
 * API 调用模块
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * 健康检查
 */
export const checkHealth = () => api.get('/health')

/**
 * 获取可用专题列表
 */
export const getTopics = () => api.get('/topics')

/**
 * 获取项目配置
 */
export const getConfig = () => api.get('/config')

/**
 * 保存项目配置
 * @param {object} config - 项目配置
 */
export const saveConfig = (config) => api.post('/config', config)

/**
 * 上传文件
 * @param {File} file - 要上传的文件
 */
export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 生成报告
 * @param {string} topicId - 专题ID
 * @param {object} config - 项目配置
 */
export const generateReport = (topicId, config) =>
  api.post('/report/generate', { topic_id: topicId, config })

/**
 * 下载报告
 * @param {string} reportId - 报告ID
 */
export const downloadReport = (reportId) =>
  api.get(`/report/download/${reportId}`, { responseType: 'blob' })

/**
 * 上传多个文件
 * @param {File[]} files - 要上传的文件列表
 */
export const uploadMultipleFiles = (files) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  return api.post('/upload/multiple', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取已上传文件列表
 */
export const getUploadedFiles = () => api.get('/upload/files')

/**
 * 获取单个已上传文件的详细信息
 * @param {string} filename - 文件名
 */
export const getUploadedFileInfo = (filename) => api.get(`/upload/files/${encodeURIComponent(filename)}`)

/**
 * 删除已上传文件
 * @param {string} filename - 文件名
 */
export const deleteUploadedFile = (filename) => api.delete(`/upload/files/${encodeURIComponent(filename)}`)

/**
 * 批量删除已上传文件
 * @param {string[]} filenames - 文件名列表
 */
export const deleteMultipleFiles = (filenames) => api.delete('/upload/files', { data: filenames })

/**
 * 获取上传文件统计
 */
export const getUploadStats = () => api.get('/upload/stats')

/**
 * 处理属性图数据
 * @param {string[]} sampleFiles - 样点文件路径列表
 * @param {string[]} areaFiles - 制图文件路径列表
 */
export const processAttributeData = (sampleFiles, areaFiles) =>
  api.post('/report/attribute-data', {
    sample_files: sampleFiles,
    area_files: areaFiles
  })

/**
 * 处理属性图上图数据
 * @param {string[]} areaFiles - 制图文件路径列表
 */
export const processMappingData = (areaFiles) =>
  api.post('/report/mapping-data', {
    area_files: areaFiles
  })

/**
 * 获取报告列表
 */
export const getReportList = () => api.get('/report/list')

/**
 * 获取处理记录列表
 */
export const getProcessRecords = () => api.get('/report/process-records')

/**
 * 获取单条处理记录详情
 * @param {string} processId - 处理ID
 */
export const getProcessRecord = (processId) => api.get(`/report/process-records/${processId}`)

/**
 * 基于处理结果生成报告
 * @param {object} params - 生成参数
 * @param {string} params.process_id - 处理ID
 * @param {string[]} params.attributes - 要包含的属性列表
 * @param {string} params.region_name - 区域名称
 * @param {number} params.survey_year - 调查年份
 * @param {string} params.theme - 图表主题
 * @param {string} params.report_mode - 报告模式: single/multi/both
 * @param {boolean} params.use_ai - 是否使用AI
 * @param {string} params.ai_provider - AI提供商
 */
export const generateReportFromProcess = (params) =>
  api.post('/report/generate-from-process', params, { timeout: 300000 })

/**
 * 下载报告文件
 * @param {string} filename - 文件名
 */
export const downloadReportFile = (filename) => {
  return `/api/report/download/${encodeURIComponent(filename)}`
}

// ============ 地区管理 API ============

/**
 * 获取地区列表
 * @param {object} params - 筛选参数
 */
export const getRegions = (params = {}) => api.get('/regions', { params })

/**
 * 创建地区
 * @param {object} data - 地区数据
 */
export const createRegion = (data) => api.post('/regions', data)

/**
 * 获取单个地区
 * @param {number} regionId - 地区ID
 */
export const getRegion = (regionId) => api.get(`/regions/${regionId}`)

/**
 * 更新地区
 * @param {number} regionId - 地区ID
 * @param {object} data - 更新数据
 */
export const updateRegion = (regionId, data) => api.put(`/regions/${regionId}`, data)

/**
 * 删除地区
 * @param {number} regionId - 地区ID
 */
export const deleteRegion = (regionId) => api.delete(`/regions/${regionId}`)

// ============ AI 配置管理 API ============

/**
 * 获取所有 AI 配置
 */
export const getAIConfigs = () => api.get('/ai-config')

/**
 * 创建 AI 配置
 * @param {object} data - 配置数据
 */
export const createAIConfig = (data) => api.post('/ai-config', data)

/**
 * 获取单个 AI 配置
 * @param {string} configId - 配置ID
 */
export const getAIConfig = (configId) => api.get(`/ai-config/${configId}`)

/**
 * 更新 AI 配置
 * @param {string} configId - 配置ID
 * @param {object} data - 更新数据
 */
export const updateAIConfig = (configId, data) => api.put(`/ai-config/${configId}`, data)

/**
 * 删除 AI 配置
 * @param {string} configId - 配置ID
 */
export const deleteAIConfig = (configId) => api.delete(`/ai-config/${configId}`)

/**
 * 设置默认 AI 配置
 * @param {string} configId - 配置ID
 */
export const setDefaultAIConfig = (configId) => api.post(`/ai-config/${configId}/set-default`)

/**
 * 测试 AI 配置
 * @param {string} configId - 配置ID
 */
export const testAIConfig = (configId) => api.post(`/ai-config/${configId}/test`)

/**
 * 获取默认 AI 配置
 */
export const getDefaultAIConfig = () => api.get('/ai-config/default/current')

export default api
