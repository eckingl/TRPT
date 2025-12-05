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

export default api
