<template>
  <div class="data-report-page">
    <div class="page-header">
      <h1>数据报告生成</h1>
      <p class="subtitle">上传数据文件，生成土壤属性统计Excel报告</p>
    </div>

    <!-- 功能说明 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <el-icon><InfoFilled /></el-icon>
          <span>报告包含以下统计表</span>
        </div>
      </template>
      <div class="table-info">
        <div class="info-group">
          <div class="group-title">制图数据统计（表1-3）</div>
          <el-tag>分乡镇统计</el-tag>
          <el-tag>土地利用类型统计</el-tag>
          <el-tag>土壤类型统计</el-tag>
        </div>
        <div class="info-group">
          <div class="group-title">样点数据统计（表4-9）</div>
          <el-tag type="success">样点统计</el-tag>
          <el-tag type="success">分行政区样点统计</el-tag>
          <el-tag type="success">土地利用类型样点统计</el-tag>
          <el-tag type="success">土壤类型样点统计</el-tag>
          <el-tag type="success">全域属性统计汇总</el-tag>
          <el-tag type="success">全域属性百分位数统计</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 数据上传区域 -->
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>数据文件上传</span>
          <el-button
            type="primary"
            text
            @click="openHistoryFileDialog"
          >
            <el-icon><FolderOpened /></el-icon>
            选择已有文件
          </el-button>
        </div>
      </template>

      <el-upload
        class="upload-area"
        drag
        multiple
        :auto-upload="false"
        :file-list="fileList"
        accept=".csv,.xlsx,.xls"
        @change="handleFileChange"
      >
        <el-icon class="el-icon--upload" :size="40"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽或<em>点击上传</em>数据文件
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 CSV、Excel 文件，最多上传2个文件</div>
        </template>
      </el-upload>

      <!-- 已上传文件列表 -->
      <div v-if="uploadedFiles.length > 0" class="uploaded-files">
        <div class="files-header">
          <span>已上传文件 ({{ uploadedFiles.length }}/2)</span>
        </div>
        <div class="file-list">
          <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
            <div class="file-info">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ file.filename }}</span>
              <span class="file-rows">{{ file.rows }} 行</span>
            </div>
            <div class="file-type">
              <el-select
                v-model="file.dataType"
                placeholder="选择数据类型"
                size="small"
                :disabled="uploadedFiles.length === 2"
              >
                <el-option label="制图数据" value="mapping" />
                <el-option label="样点数据" value="sample" />
              </el-select>
            </div>
            <el-button text type="danger" @click="removeFile(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 两个文件时的提示 -->
        <el-alert
          v-if="uploadedFiles.length === 2"
          title="已上传2个文件，将分别作为制图数据和样点数据处理"
          type="info"
          show-icon
          :closable="false"
          class="two-files-tip"
        />

        <!-- 单文件时的说明 -->
        <el-alert
          v-if="uploadedFiles.length === 1"
          :title="singleFileHint"
          type="info"
          show-icon
          :closable="false"
          class="single-file-tip"
        />
      </div>

      <div class="action-section">
        <el-alert
          v-if="uploadedFiles.length === 0"
          title="请上传数据文件（1-2个）"
          type="warning"
          show-icon
          :closable="false"
        />
        <el-button
          v-else
          type="primary"
          size="large"
          :loading="processing"
          :disabled="!canGenerate"
          @click="generateDataReport"
        >
          <el-icon><VideoPlay /></el-icon>
          生成数据报告
        </el-button>
      </div>
    </el-card>

    <!-- 处理结果 -->
    <el-card v-if="processResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>处理结果</span>
          <el-tag v-if="processResult.success" type="success">成功</el-tag>
          <el-tag v-else type="danger">失败</el-tag>
        </div>
      </template>

      <div v-if="!processResult.success" class="error-message">
        <el-alert :title="processResult.message" type="error" show-icon :closable="false" />
      </div>

      <div v-else>
        <el-result
          icon="success"
          title="数据报告生成成功"
          :sub-title="processResult.message"
        >
          <template #extra>
            <el-button type="primary" size="large" @click="downloadResult">
              <el-icon><Download /></el-icon>
              下载 Excel 报告
            </el-button>
            <el-button @click="clearResult">
              重新生成
            </el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <!-- 文件下载历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>历史报告</span>
          <el-button text @click="refreshHistory">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div v-if="reportList.length > 0" class="history-list">
        <el-table :data="reportList" stripe>
          <el-table-column prop="filename" label="文件名" min-width="250" />
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
      <el-empty v-else description="暂无历史报告" />
    </el-card>

    <div class="page-actions">
      <el-button @click="$router.push('/')">
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </el-button>
    </div>

    <!-- 历史文件选择对话框 -->
    <el-dialog
      v-model="showHistoryFileDialog"
      title="选择已上传的文件"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-loading="loadingHistoryFiles" class="history-file-content">
        <el-alert
          v-if="historyFiles.length === 0 && !loadingHistoryFiles"
          title="暂无已上传的文件"
          type="info"
          show-icon
          :closable="false"
        />
        <el-table
          v-else
          ref="historyTableRef"
          :data="historyFiles"
          stripe
          max-height="400px"
          @selection-change="handleHistorySelectionChange"
        >
          <el-table-column type="selection" width="50" :selectable="canSelectFile" />
          <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
          <el-table-column label="行数" width="80">
            <template #default="{ row }">
              {{ row.rows || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="上传时间" width="170" />
        </el-table>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showHistoryFileDialog = false">取消</el-button>
          <el-button
            type="primary"
            :disabled="selectedHistoryFiles.length === 0"
            @click="confirmSelectHistoryFiles"
          >
            确认选择 ({{ selectedHistoryFiles.length }})
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Document,
  QuestionFilled,
  UploadFilled,
  Delete,
  VideoPlay,
  Download,
  Refresh,
  ArrowLeft,
  FolderOpened,
  InfoFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  uploadFile as apiUploadFile,
  generateDataReport as apiGenerateDataReport,
  getReportList,
  getUploadedFiles,
  getUploadedFileInfo
} from '@/api'

const processing = ref(false)
const processResult = ref(null)
const reportList = ref([])

// 文件上传
const fileList = ref([])
const uploadedFiles = ref([])  // { filename, rows, file_path, dataType: 'mapping' | 'sample' }

// 历史文件选择对话框
const showHistoryFileDialog = ref(false)
const historyFiles = ref([])
const loadingHistoryFiles = ref(false)
const selectedHistoryFiles = ref([])
const historyTableRef = ref(null)

// 计算属性：单文件时的提示
const singleFileHint = computed(() => {
  if (uploadedFiles.value.length !== 1) return ''
  const file = uploadedFiles.value[0]
  if (file.dataType === 'mapping') {
    return '当前文件将作为制图数据处理，生成表1-3'
  } else if (file.dataType === 'sample') {
    return '当前文件将作为样点数据处理，生成表4-9'
  }
  return '请选择数据类型'
})

// 计算属性：是否可以生成报告
const canGenerate = computed(() => {
  if (uploadedFiles.value.length === 0) return false
  if (uploadedFiles.value.length === 1) {
    return uploadedFiles.value[0].dataType !== undefined
  }
  return true
})

// 处理文件上传
const handleFileChange = async (fileInfo) => {
  const file = fileInfo.raw
  if (!file) return

  // 检查文件数量限制
  if (uploadedFiles.value.length >= 2) {
    ElMessage.warning('最多只能上传2个文件')
    fileList.value = []
    return
  }

  try {
    const result = await apiUploadFile(file)

    // 设置默认数据类型
    let dataType = undefined
    if (uploadedFiles.value.length === 0) {
      // 第一个文件，默认为样点数据
      dataType = 'sample'
    } else {
      // 第二个文件，自动设置为另一种类型
      const firstType = uploadedFiles.value[0].dataType
      dataType = firstType === 'mapping' ? 'sample' : 'mapping'
      // 同时确保第一个文件也有类型
      if (!uploadedFiles.value[0].dataType) {
        uploadedFiles.value[0].dataType = 'mapping'
      }
    }

    uploadedFiles.value.push({
      ...result,
      dataType
    })
    ElMessage.success(`文件 ${result.filename} 上传成功`)
  } catch (error) {
    ElMessage.error(error.message || '文件上传失败')
  }
  fileList.value = []
}

// 移除文件
const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

// 打开历史文件选择对话框
const openHistoryFileDialog = async () => {
  selectedHistoryFiles.value = []
  showHistoryFileDialog.value = true
  loadingHistoryFiles.value = true

  try {
    const response = await getUploadedFiles()
    historyFiles.value = response.files || []
  } catch (error) {
    ElMessage.error('获取历史文件列表失败')
    historyFiles.value = []
  } finally {
    loadingHistoryFiles.value = false
  }
}

// 是否可以选择文件（最多选2个）
const canSelectFile = () => {
  const currentCount = uploadedFiles.value.length
  const selectedCount = selectedHistoryFiles.value.length
  return (currentCount + selectedCount) < 2 || selectedHistoryFiles.value.length > 0
}

// 处理历史文件选择变化
const handleHistorySelectionChange = (rows) => {
  const maxSelect = 2 - uploadedFiles.value.length
  if (rows.length > maxSelect) {
    // 超过限制，取消最后选择的
    ElMessage.warning(`最多只能再选择 ${maxSelect} 个文件`)
    // 保留前 maxSelect 个
    const toKeep = rows.slice(0, maxSelect)
    selectedHistoryFiles.value = toKeep.map(r => r.filename)
    // 更新表格选择状态
    if (historyTableRef.value) {
      historyTableRef.value.clearSelection()
      toKeep.forEach(row => {
        historyTableRef.value.toggleRowSelection(row, true)
      })
    }
  } else {
    selectedHistoryFiles.value = rows.map(r => r.filename)
  }
}

// 确认选择历史文件
const confirmSelectHistoryFiles = async () => {
  if (selectedHistoryFiles.value.length === 0) {
    ElMessage.warning('请至少选择一个文件')
    return
  }

  for (const filename of selectedHistoryFiles.value) {
    if (uploadedFiles.value.length >= 2) break

    try {
      const fileInfo = await getUploadedFileInfo(filename)

      const exists = uploadedFiles.value.some(f => f.file_path === fileInfo.file_path)
      if (exists) {
        ElMessage.warning(`文件 ${filename} 已添加`)
        continue
      }

      // 设置默认数据类型
      let dataType = undefined
      if (uploadedFiles.value.length === 0) {
        dataType = 'sample'
      } else {
        const firstType = uploadedFiles.value[0].dataType
        dataType = firstType === 'mapping' ? 'sample' : 'mapping'
        if (!uploadedFiles.value[0].dataType) {
          uploadedFiles.value[0].dataType = 'mapping'
        }
      }

      uploadedFiles.value.push({
        ...fileInfo,
        dataType
      })
    } catch (error) {
      ElMessage.error(`获取文件 ${filename} 信息失败`)
    }
  }

  showHistoryFileDialog.value = false
  ElMessage.success(`已添加 ${selectedHistoryFiles.value.length} 个文件`)
}

// 生成数据报告
const generateDataReport = async () => {
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning('请上传数据文件')
    return
  }

  // 检查单文件时是否选择了类型
  if (uploadedFiles.value.length === 1 && !uploadedFiles.value[0].dataType) {
    ElMessage.warning('请选择数据类型')
    return
  }

  processing.value = true
  processResult.value = null

  try {
    // 根据用户选择的文件类型分配
    let mappingPaths = []
    let samplePaths = []

    for (const file of uploadedFiles.value) {
      if (file.dataType === 'mapping') {
        mappingPaths.push(file.file_path)
      } else if (file.dataType === 'sample') {
        samplePaths.push(file.file_path)
      }
    }

    console.log('生成数据报告参数:', { mappingPaths, samplePaths, files: uploadedFiles.value })

    const result = await apiGenerateDataReport(mappingPaths, samplePaths)
    processResult.value = result

    if (result.success) {
      ElMessage.success('数据报告生成成功')
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
    const list = await getReportList()
    // 只显示数据报告相关的文件
    reportList.value = list.filter(f => f.filename.includes('数据报告'))
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (!bytes) return '-'
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
.data-report-page {
  max-width: 900px;
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

/* 信息卡片 */
.info-card {
  margin-bottom: 20px;
}

.info-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
}

.table-info {
  display: flex;
  gap: 40px;
}

.info-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.group-title {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
}

/* 上传卡片 */
.upload-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 17px;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  padding: 40px 20px;
}

/* 已上传文件 */
.uploaded-files {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.files-header {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 12px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.file-info .el-icon {
  color: #409eff;
}

.file-name {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.file-rows {
  font-size: 12px;
  color: #909399;
}

.file-type {
  width: 130px;
}

.two-files-tip,
.single-file-tip {
  margin-top: 12px;
}

/* 操作区域 */
.action-section {
  margin-top: 24px;
  text-align: center;
}

/* 结果卡片 */
.result-card {
  margin-bottom: 20px;
}

.error-message {
  padding: 20px 0;
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

/* 历史文件对话框 */
.history-file-content {
  min-height: 200px;
}

/* 响应式 */
@media (max-width: 768px) {
  .table-info {
    flex-direction: column;
    gap: 16px;
  }

  .file-item {
    flex-wrap: wrap;
  }

  .file-info {
    width: 100%;
  }

  .file-type {
    width: 100%;
  }
}
</style>
