<template>
  <div class="attribute-process-page">
    <div class="page-header">
      <h1>属性图数据处理</h1>
      <p class="subtitle">选择功能并上传数据文件进行处理</p>
    </div>

    <!-- 功能选择 -->
    <div class="function-selector">
      <div
        class="function-card"
        :class="{ active: currentFunction === 'attribute' }"
        @click="selectFunction('attribute')"
      >
        <el-icon :size="36"><DataAnalysis /></el-icon>
        <div class="function-info">
          <span class="function-title">属性图数据处理</span>
          <span class="function-desc">合并样点统计与制图统计数据，生成属性分级统计表</span>
        </div>
      </div>
      <div
        class="function-card"
        :class="{ active: currentFunction === 'mapping' }"
        @click="selectFunction('mapping')"
      >
        <el-icon :size="36"><MapLocation /></el-icon>
        <div class="function-info">
          <span class="function-title">属性图上图处理</span>
          <span class="function-desc">处理制图统计数据，生成面积统计表</span>
        </div>
      </div>
    </div>

    <!-- 属性图数据处理区域 -->
    <el-card v-if="currentFunction === 'attribute'" class="process-card">
      <template #header>
        <div class="card-header">
          <span>属性图数据处理</span>
          <el-tag type="info">需要样点+制图文件</el-tag>
        </div>
      </template>

      <div class="upload-section">
        <!-- 样点统计文件上传 -->
        <div class="file-group">
          <div class="group-header">
            <el-icon><Document /></el-icon>
            <span>样点统计文件</span>
            <el-tooltip content="包含土壤养分、pH等属性数据的样点统计CSV文件">
              <el-icon class="help-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-upload
            class="upload-area"
            drag
            multiple
            :auto-upload="false"
            :file-list="sampleFiles"
            accept=".csv"
            @change="handleSampleFileChange"
          >
            <el-icon class="el-icon--upload" :size="40"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽或<em>点击上传</em>样点统计文件
            </div>
            <template #tip>
              <div class="el-upload__tip">支持多个 CSV 文件</div>
            </template>
          </el-upload>
          <div v-if="uploadedSampleFiles.length > 0" class="file-list">
            <div v-for="(file, index) in uploadedSampleFiles" :key="index" class="file-item">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ file.filename }}</span>
              <span class="file-rows">{{ file.rows }} 行</span>
              <el-button text type="danger" @click="removeSampleFile(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 制图统计文件上传 -->
        <div class="file-group">
          <div class="group-header">
            <el-icon><Document /></el-icon>
            <span>制图统计文件</span>
            <el-tooltip content="包含土地利用类型、乡镇、面积等数据的制图统计CSV文件">
              <el-icon class="help-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-upload
            class="upload-area"
            drag
            multiple
            :auto-upload="false"
            :file-list="areaFiles"
            accept=".csv"
            @change="handleAreaFileChange"
          >
            <el-icon class="el-icon--upload" :size="40"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽或<em>点击上传</em>制图统计文件
            </div>
            <template #tip>
              <div class="el-upload__tip">支持多个 CSV 文件</div>
            </template>
          </el-upload>
          <div v-if="uploadedAreaFiles.length > 0" class="file-list">
            <div v-for="(file, index) in uploadedAreaFiles" :key="index" class="file-item">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ file.filename }}</span>
              <span class="file-rows">{{ file.rows }} 行</span>
              <el-button text type="danger" @click="removeAreaFile(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="action-section">
        <el-button
          type="primary"
          size="large"
          :loading="processing"
          :disabled="uploadedSampleFiles.length === 0 || uploadedAreaFiles.length === 0"
          @click="processAttributeData"
        >
          <el-icon><VideoPlay /></el-icon>
          开始处理
        </el-button>
      </div>
    </el-card>

    <!-- 属性图上图处理区域 -->
    <el-card v-if="currentFunction === 'mapping'" class="process-card">
      <template #header>
        <div class="card-header">
          <span>属性图上图处理</span>
          <el-tag type="info">仅需制图文件</el-tag>
        </div>
      </template>

      <div class="upload-section">
        <div class="file-group single">
          <div class="group-header">
            <el-icon><Document /></el-icon>
            <span>制图统计文件</span>
            <el-tooltip content="包含土地利用类型、乡镇、面积等数据的制图统计CSV文件">
              <el-icon class="help-icon"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-upload
            class="upload-area"
            drag
            multiple
            :auto-upload="false"
            :file-list="mappingFiles"
            accept=".csv"
            @change="handleMappingFileChange"
          >
            <el-icon class="el-icon--upload" :size="40"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽或<em>点击上传</em>制图统计文件
            </div>
            <template #tip>
              <div class="el-upload__tip">支持多个 CSV 文件</div>
            </template>
          </el-upload>
          <div v-if="uploadedMappingFiles.length > 0" class="file-list">
            <div v-for="(file, index) in uploadedMappingFiles" :key="index" class="file-item">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ file.filename }}</span>
              <span class="file-rows">{{ file.rows }} 行</span>
              <el-button text type="danger" @click="removeMappingFile(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="action-section">
        <el-button
          type="primary"
          size="large"
          :loading="processing"
          :disabled="uploadedMappingFiles.length === 0"
          @click="processMappingData"
        >
          <el-icon><VideoPlay /></el-icon>
          开始处理
        </el-button>
      </div>
    </el-card>

    <!-- 处理结果 -->
    <el-card v-if="processResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>处理结果</span>
        </div>
      </template>
      <el-result
        :icon="processResult.success ? 'success' : 'error'"
        :title="processResult.success ? '处理完成' : '处理失败'"
        :sub-title="processResult.message"
      >
        <template #extra>
          <el-button
            v-if="processResult.success && processResult.download_url"
            type="primary"
            @click="downloadResult"
          >
            <el-icon><Download /></el-icon>
            下载结果文件
          </el-button>
          <el-button @click="clearResult">
            继续处理
          </el-button>
        </template>
      </el-result>
    </el-card>

    <!-- 历史记录 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>历史记录</span>
          <el-button text @click="refreshHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div v-if="reportList.length > 0" class="history-list">
        <el-table :data="reportList" stripe>
          <el-table-column prop="filename" label="文件名" min-width="200" />
          <el-table-column prop="size" label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="downloadFile(row.download_url)">
                <el-icon><Download /></el-icon>
                下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无历史记录" />
    </el-card>

    <div class="page-actions">
      <el-button @click="$router.push('/')">
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  DataAnalysis,
  MapLocation,
  Document,
  QuestionFilled,
  UploadFilled,
  Delete,
  VideoPlay,
  Download,
  Refresh,
  ArrowLeft
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  uploadFile as apiUploadFile,
  processAttributeData as apiProcessAttributeData,
  processMappingData as apiProcessMappingData,
  getReportList
} from '@/api'

const currentFunction = ref('attribute')
const processing = ref(false)
const processResult = ref(null)
const reportList = ref([])

// 属性图数据处理的文件
const sampleFiles = ref([])
const areaFiles = ref([])
const uploadedSampleFiles = ref([])
const uploadedAreaFiles = ref([])

// 属性图上图处理的文件
const mappingFiles = ref([])
const uploadedMappingFiles = ref([])

const selectFunction = (func) => {
  currentFunction.value = func
  processResult.value = null
}

// 处理样点文件上传
const handleSampleFileChange = async (fileInfo) => {
  const file = fileInfo.raw
  if (!file) return

  try {
    const result = await apiUploadFile(file)
    uploadedSampleFiles.value.push(result)
    ElMessage.success(`文件 ${result.filename} 上传成功`)
  } catch (error) {
    ElMessage.error(error.message || '文件上传失败')
  }
  // 清空 el-upload 的 file-list
  sampleFiles.value = []
}

// 处理制图文件上传（属性图数据处理）
const handleAreaFileChange = async (fileInfo) => {
  const file = fileInfo.raw
  if (!file) return

  try {
    const result = await apiUploadFile(file)
    uploadedAreaFiles.value.push(result)
    ElMessage.success(`文件 ${result.filename} 上传成功`)
  } catch (error) {
    ElMessage.error(error.message || '文件上传失败')
  }
  areaFiles.value = []
}

// 处理制图文件上传（属性图上图处理）
const handleMappingFileChange = async (fileInfo) => {
  const file = fileInfo.raw
  if (!file) return

  try {
    const result = await apiUploadFile(file)
    uploadedMappingFiles.value.push(result)
    ElMessage.success(`文件 ${result.filename} 上传成功`)
  } catch (error) {
    ElMessage.error(error.message || '文件上传失败')
  }
  mappingFiles.value = []
}

// 移除文件
const removeSampleFile = (index) => {
  uploadedSampleFiles.value.splice(index, 1)
}

const removeAreaFile = (index) => {
  uploadedAreaFiles.value.splice(index, 1)
}

const removeMappingFile = (index) => {
  uploadedMappingFiles.value.splice(index, 1)
}

// 执行属性图数据处理
const processAttributeData = async () => {
  if (uploadedSampleFiles.value.length === 0 || uploadedAreaFiles.value.length === 0) {
    ElMessage.warning('请先上传样点统计文件和制图统计文件')
    return
  }

  processing.value = true
  processResult.value = null

  try {
    const samplePaths = uploadedSampleFiles.value.map(f => f.file_path)
    const areaPaths = uploadedAreaFiles.value.map(f => f.file_path)
    const result = await apiProcessAttributeData(samplePaths, areaPaths)
    processResult.value = result
    if (result.success) {
      ElMessage.success('数据处理完成')
      refreshHistory()
    }
  } catch (error) {
    processResult.value = {
      success: false,
      message: error.message || '处理失败'
    }
    ElMessage.error(error.message || '处理失败')
  } finally {
    processing.value = false
  }
}

// 执行属性图上图处理
const processMappingData = async () => {
  if (uploadedMappingFiles.value.length === 0) {
    ElMessage.warning('请先上传制图统计文件')
    return
  }

  processing.value = true
  processResult.value = null

  try {
    const areaPaths = uploadedMappingFiles.value.map(f => f.file_path)
    const result = await apiProcessMappingData(areaPaths)
    processResult.value = result
    if (result.success) {
      ElMessage.success('数据处理完成')
      refreshHistory()
    }
  } catch (error) {
    processResult.value = {
      success: false,
      message: error.message || '处理失败'
    }
    ElMessage.error(error.message || '处理失败')
  } finally {
    processing.value = false
  }
}

// 下载结果
const downloadResult = () => {
  if (processResult.value?.download_url) {
    window.open(processResult.value.download_url, '_blank')
  }
}

// 下载文件
const downloadFile = (url) => {
  window.open(url, '_blank')
}

// 清除结果
const clearResult = () => {
  processResult.value = null
}

// 刷新历史记录
const refreshHistory = async () => {
  try {
    reportList.value = await getReportList()
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.attribute-process-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px;
  font-size: 26px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 15px;
  margin: 0;
}

/* 功能选择器 */
.function-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.function-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.function-card:hover {
  border-color: var(--el-color-primary-light-3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.function-card.active {
  border-color: var(--el-color-primary);
  background: linear-gradient(135deg, #ecf5ff 0%, #fff 100%);
}

.function-card .el-icon {
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.function-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.function-title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
}

.function-desc {
  font-size: 13px;
  color: #909399;
}

/* 处理卡片 */
.process-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 17px;
  font-weight: 600;
}

/* 上传区域 */
.upload-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.file-group.single {
  grid-column: span 2;
  max-width: 500px;
  margin: 0 auto;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.help-icon {
  color: #909399;
  cursor: help;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 30px 20px;
}

/* 文件列表 */
.file-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f5f7fa;
  border-radius: 6px;
}

.file-item .el-icon {
  color: #409eff;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-rows {
  font-size: 12px;
  color: #909399;
}

/* 操作区域 */
.action-section {
  margin-top: 30px;
  text-align: center;
}

/* 结果卡片 */
.result-card {
  margin-bottom: 20px;
}

/* 历史记录卡片 */
.history-card {
  margin-bottom: 20px;
}

.history-list {
  max-height: 300px;
  overflow: auto;
}

/* 页面操作 */
.page-actions {
  margin-top: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .function-selector {
    grid-template-columns: 1fr;
  }

  .upload-section {
    grid-template-columns: 1fr;
  }

  .file-group.single {
    max-width: none;
  }
}
</style>
