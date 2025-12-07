<template>
  <div class="data-manage-container">
    <el-card class="stats-card">
      <template #header>
        <div class="card-header">
          <span>数据库统计</span>
          <el-button type="primary" size="small" @click="loadStats">刷新</el-button>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="4">
          <el-statistic title="地区数量" :value="stats.regions_count" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="数据记录" :value="stats.data_count" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="配置数量" :value="stats.config_count" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="数据库大小" :value="stats.db_size_mb" suffix="MB" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="已上传文件" :value="uploadStats.total_files" />
        </el-col>
        <el-col :span="4">
          <el-statistic title="上传文件大小" :value="uploadStats.total_size_readable" />
        </el-col>
      </el-row>
    </el-card>

    <el-tabs v-model="activeTab" class="data-tabs">
      <!-- 地区管理 -->
      <el-tab-pane label="地区管理" name="regions">
        <div class="tab-toolbar">
          <el-select v-model="regionFilter.category" placeholder="按类别筛选" clearable @change="loadRegions">
            <el-option label="土壤普查" value="soil_survey" />
            <el-option label="土地质量" value="land_quality" />
          </el-select>
          <el-select v-model="regionFilter.topic" placeholder="按专题筛选" clearable @change="loadRegions" style="margin-left: 10px">
            <el-option label="属性图" value="attribute_map" />
            <el-option label="类型图" value="type_map" />
            <el-option label="适宜性" value="suitability" />
          </el-select>
          <el-button type="danger" :disabled="selectedRegions.length === 0" @click="batchDeleteRegions" style="margin-left: 10px">
            批量删除 ({{ selectedRegions.length }})
          </el-button>
        </div>

        <el-table :data="regions" @selection-change="handleRegionSelectionChange" v-loading="loadingRegions">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column prop="category" label="类别" width="100" />
          <el-table-column prop="topic" label="专题" width="120" />
          <el-table-column prop="province" label="省份" width="100" />
          <el-table-column prop="city" label="城市" width="100" />
          <el-table-column prop="county" label="区县" width="100" />
          <el-table-column prop="updated_at" label="更新时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewRegionDetail(row)">详情</el-button>
              <el-button type="warning" size="small" @click="editRegion(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="deleteRegion(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="regionPagination.page"
          v-model:page-size="regionPagination.pageSize"
          :total="regionPagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadRegions"
          @current-change="loadRegions"
          style="margin-top: 20px"
        />
      </el-tab-pane>

      <!-- 项目数据管理 -->
      <el-tab-pane label="项目数据" name="project-data">
        <div class="tab-toolbar">
          <el-select v-model="dataFilter.region_id" placeholder="按地区筛选" clearable @change="loadProjectData">
            <el-option v-for="r in allRegions" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
          <el-select v-model="dataFilter.data_type" placeholder="按类型筛选" clearable @change="loadProjectData" style="margin-left: 10px">
            <el-option label="原始数据" value="raw_data" />
            <el-option label="处理数据" value="processed_data" />
            <el-option label="图表数据" value="chart_data" />
          </el-select>
          <el-button type="danger" :disabled="selectedData.length === 0" @click="batchDeleteData" style="margin-left: 10px">
            批量删除 ({{ selectedData.length }})
          </el-button>
        </div>

        <el-table :data="projectData" @selection-change="handleDataSelectionChange" v-loading="loadingData">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="region_name" label="所属地区" width="150" />
          <el-table-column prop="data_type" label="数据类型" width="120" />
          <el-table-column prop="file_name" label="文件名" width="200" />
          <el-table-column label="数据大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.data_size) }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewDataDetail(row)">查看</el-button>
              <el-button type="warning" size="small" @click="editData(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="deleteData(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="dataPagination.page"
          v-model:page-size="dataPagination.pageSize"
          :total="dataPagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadProjectData"
          @current-change="loadProjectData"
          style="margin-top: 20px"
        />
      </el-tab-pane>

      <!-- 已上传文件管理 -->
      <el-tab-pane label="已上传文件" name="uploaded-files">
        <div class="tab-toolbar">
          <el-input
            v-model="uploadFileSearch"
            placeholder="搜索文件名"
            style="width: 250px"
            clearable
            @input="filterUploadedFiles"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="danger" :disabled="selectedUploadedFiles.length === 0" @click="batchDeleteUploadedFiles" style="margin-left: 10px">
            批量删除 ({{ selectedUploadedFiles.length }})
          </el-button>
          <el-button @click="loadUploadedFiles" style="margin-left: auto">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <el-table :data="filteredUploadedFiles" @selection-change="handleUploadedFileSelectionChange" v-loading="loadingUploadedFiles">
          <el-table-column type="selection" width="50" />
          <el-table-column prop="filename" label="文件名" min-width="250" show-overflow-tooltip />
          <el-table-column label="行数" width="100">
            <template #default="{ row }">
              {{ row.rows ? row.rows.toLocaleString() : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="文件大小" width="120">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="upload_time" label="上传时间" width="180" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewUploadedFileDetail(row)">查看</el-button>
              <el-button type="danger" size="small" @click="deleteUploadedFile(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="upload-summary">
          共 {{ uploadedFiles.length }} 个文件，占用空间 {{ uploadStats.total_size_readable }}
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 地区详情对话框 -->
    <el-dialog v-model="regionDetailVisible" title="地区详情" width="80%">
      <el-descriptions :column="3" border v-if="currentRegion">
        <el-descriptions-item label="ID">{{ currentRegion.id }}</el-descriptions-item>
        <el-descriptions-item label="名称">{{ currentRegion.name }}</el-descriptions-item>
        <el-descriptions-item label="类别">{{ currentRegion.category }}</el-descriptions-item>
        <el-descriptions-item label="专题">{{ currentRegion.topic }}</el-descriptions-item>
        <el-descriptions-item label="省份">{{ currentRegion.province || '-' }}</el-descriptions-item>
        <el-descriptions-item label="城市">{{ currentRegion.city || '-' }}</el-descriptions-item>
        <el-descriptions-item label="区县">{{ currentRegion.county || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentRegion.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ currentRegion.updated_at }}</el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px">关联数据</h4>
      <el-table :data="regionDetailData" style="margin-top: 10px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="data_type" label="类型" width="120" />
        <el-table-column prop="file_name" label="文件名" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
      </el-table>

      <h4 style="margin-top: 20px">配置信息</h4>
      <el-input
        v-model="regionConfigJson"
        type="textarea"
        :rows="6"
        readonly
        placeholder="无配置"
      />
    </el-dialog>

    <!-- 编辑地区对话框 -->
    <el-dialog v-model="editRegionVisible" title="编辑地区" width="400px">
      <el-form :model="editRegionForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="editRegionForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editRegionVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRegion">保存</el-button>
      </template>
    </el-dialog>

    <!-- 数据详情对话框 -->
    <el-dialog v-model="dataDetailVisible" title="数据详情" width="80%">
      <el-descriptions :column="2" border v-if="currentData">
        <el-descriptions-item label="ID">{{ currentData.id }}</el-descriptions-item>
        <el-descriptions-item label="所属地区">{{ currentData.region_name }}</el-descriptions-item>
        <el-descriptions-item label="数据类型">{{ currentData.data_type }}</el-descriptions-item>
        <el-descriptions-item label="文件名">{{ currentData.file_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentData.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ currentData.updated_at }}</el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px">数据内容</h4>
      <el-input
        v-model="currentDataContent"
        type="textarea"
        :rows="15"
        :readonly="!editingData"
      />
      <template #footer>
        <el-button v-if="!editingData" @click="editingData = true">编辑</el-button>
        <el-button v-if="editingData" @click="editingData = false">取消编辑</el-button>
        <el-button v-if="editingData" type="primary" @click="saveDataContent">保存</el-button>
        <el-button @click="dataDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 已上传文件详情对话框 -->
    <el-dialog v-model="uploadedFileDetailVisible" title="文件详情" width="80%">
      <el-descriptions :column="3" border v-if="currentUploadedFile">
        <el-descriptions-item label="文件名">{{ currentUploadedFile.filename }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatSize(currentUploadedFile.size) }}</el-descriptions-item>
        <el-descriptions-item label="上传时间">{{ currentUploadedFile.upload_time }}</el-descriptions-item>
        <el-descriptions-item label="数据行数">{{ currentUploadedFile.rows?.toLocaleString() || '-' }}</el-descriptions-item>
        <el-descriptions-item label="列数">{{ currentUploadedFile.columns?.length || '-' }}</el-descriptions-item>
        <el-descriptions-item label="文件路径">{{ currentUploadedFile.file_path }}</el-descriptions-item>
      </el-descriptions>

      <h4 style="margin-top: 20px">列信息</h4>
      <div class="columns-list" v-if="currentUploadedFile?.columns">
        <el-tag v-for="col in currentUploadedFile.columns" :key="col" style="margin: 4px">
          {{ col }}
        </el-tag>
      </div>

      <h4 style="margin-top: 20px">数据预览（前10行）</h4>
      <el-table :data="currentUploadedFile?.preview || []" style="margin-top: 10px" max-height="300">
        <el-table-column
          v-for="col in currentUploadedFile?.columns || []"
          :key="col"
          :prop="col"
          :label="col"
          min-width="120"
          show-overflow-tooltip
        />
      </el-table>

      <template #footer>
        <el-button type="danger" @click="deleteUploadedFileFromDialog">删除此文件</el-button>
        <el-button @click="uploadedFileDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import axios from 'axios'
import {
  getUploadedFiles,
  getUploadedFileInfo,
  deleteUploadedFile as apiDeleteUploadedFile,
  deleteMultipleFiles,
  getUploadStats
} from '@/api'

const API_BASE = '/api/data-manage'

// 统计数据
const stats = ref({
  regions_count: 0,
  data_count: 0,
  config_count: 0,
  db_size_mb: 0
})

// 上传文件统计
const uploadStats = ref({
  total_files: 0,
  total_size: 0,
  total_size_readable: '0 B',
  file_types: {}
})

// Tab
const activeTab = ref('regions')

// 地区数据
const regions = ref([])
const allRegions = ref([])
const loadingRegions = ref(false)
const selectedRegions = ref([])
const regionFilter = ref({ category: '', topic: '' })
const regionPagination = ref({ page: 1, pageSize: 20, total: 0 })

// 项目数据
const projectData = ref([])
const loadingData = ref(false)
const selectedData = ref([])
const dataFilter = ref({ region_id: null, data_type: '' })
const dataPagination = ref({ page: 1, pageSize: 20, total: 0 })

// 对话框
const regionDetailVisible = ref(false)
const currentRegion = ref(null)
const regionDetailData = ref([])
const regionConfigJson = ref('')

const editRegionVisible = ref(false)
const editRegionForm = ref({ id: null, name: '' })

const dataDetailVisible = ref(false)
const currentData = ref(null)
const currentDataContent = ref('')
const editingData = ref(false)

// 已上传文件
const uploadedFiles = ref([])
const loadingUploadedFiles = ref(false)
const selectedUploadedFiles = ref([])
const uploadFileSearch = ref('')
const uploadedFileDetailVisible = ref(false)
const currentUploadedFile = ref(null)

// 过滤后的文件列表
const filteredUploadedFiles = computed(() => {
  if (!uploadFileSearch.value) {
    return uploadedFiles.value
  }
  const keyword = uploadFileSearch.value.toLowerCase()
  return uploadedFiles.value.filter(f =>
    f.filename.toLowerCase().includes(keyword)
  )
})

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await axios.get(`${API_BASE}/stats`)
    stats.value = res.data
  } catch (err) {
    ElMessage.error('加载统计数据失败')
  }
}

// 加载地区列表
const loadRegions = async () => {
  loadingRegions.value = true
  try {
    const params = {
      page: regionPagination.value.page,
      page_size: regionPagination.value.pageSize
    }
    if (regionFilter.value.category) params.category = regionFilter.value.category
    if (regionFilter.value.topic) params.topic = regionFilter.value.topic

    const res = await axios.get(`${API_BASE}/regions`, { params })
    regions.value = res.data.items
    regionPagination.value.total = res.data.total
  } catch (err) {
    ElMessage.error('加载地区列表失败')
  } finally {
    loadingRegions.value = false
  }
}

// 加载所有地区（用于筛选下拉）
const loadAllRegions = async () => {
  try {
    const res = await axios.get(`${API_BASE}/regions`, { params: { page_size: 1000 } })
    allRegions.value = res.data.items
  } catch (err) {
    console.error('加载所有地区失败')
  }
}

// 加载项目数据
const loadProjectData = async () => {
  loadingData.value = true
  try {
    const params = {
      page: dataPagination.value.page,
      page_size: dataPagination.value.pageSize
    }
    if (dataFilter.value.region_id) params.region_id = dataFilter.value.region_id
    if (dataFilter.value.data_type) params.data_type = dataFilter.value.data_type

    const res = await axios.get(`${API_BASE}/project-data`, { params })
    projectData.value = res.data.items
    dataPagination.value.total = res.data.total
  } catch (err) {
    ElMessage.error('加载项目数据失败')
  } finally {
    loadingData.value = false
  }
}

// 查看地区详情
const viewRegionDetail = async (row) => {
  try {
    const res = await axios.get(`${API_BASE}/regions/${row.id}`)
    currentRegion.value = res.data.region
    regionDetailData.value = res.data.project_data || []
    regionConfigJson.value = res.data.config ? JSON.stringify(res.data.config, null, 2) : ''
    regionDetailVisible.value = true
  } catch (err) {
    ElMessage.error('加载地区详情失败')
  }
}

// 编辑地区
const editRegion = (row) => {
  editRegionForm.value = { id: row.id, name: row.name }
  editRegionVisible.value = true
}

// 保存地区
const saveRegion = async () => {
  try {
    await axios.put(`${API_BASE}/regions/${editRegionForm.value.id}`, {
      name: editRegionForm.value.name
    })
    ElMessage.success('保存成功')
    editRegionVisible.value = false
    loadRegions()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

// 删除地区
const deleteRegion = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除地区 "${row.name}" 吗？此操作将同时删除所有关联数据。`, '确认删除', {
      type: 'warning'
    })
    await axios.delete(`${API_BASE}/regions/${row.id}`)
    ElMessage.success('删除成功')
    loadRegions()
    loadStats()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除地区
const batchDeleteRegions = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRegions.value.length} 个地区吗？`, '确认删除', {
      type: 'warning'
    })
    const ids = selectedRegions.value.map(r => r.id)
    await axios.post(`${API_BASE}/batch-delete/regions`, ids)
    ElMessage.success('批量删除成功')
    loadRegions()
    loadStats()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 查看数据详情
const viewDataDetail = async (row) => {
  try {
    const res = await axios.get(`${API_BASE}/project-data/${row.id}`)
    currentData.value = res.data
    currentDataContent.value = res.data.data_content || ''
    editingData.value = false
    dataDetailVisible.value = true
  } catch (err) {
    ElMessage.error('加载数据详情失败')
  }
}

// 编辑数据
const editData = (row) => {
  viewDataDetail(row)
  setTimeout(() => {
    editingData.value = true
  }, 100)
}

// 保存数据内容
const saveDataContent = async () => {
  try {
    await axios.put(`${API_BASE}/project-data/${currentData.value.id}`, {
      data_content: currentDataContent.value
    })
    ElMessage.success('保存成功')
    editingData.value = false
    loadProjectData()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

// 删除数据
const deleteData = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这条数据吗？', '确认删除', {
      type: 'warning'
    })
    await axios.delete(`${API_BASE}/project-data/${row.id}`)
    ElMessage.success('删除成功')
    loadProjectData()
    loadStats()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 批量删除数据
const batchDeleteData = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedData.value.length} 条数据吗？`, '确认删除', {
      type: 'warning'
    })
    const ids = selectedData.value.map(d => d.id)
    await axios.post(`${API_BASE}/batch-delete/project-data`, ids)
    ElMessage.success('批量删除成功')
    loadProjectData()
    loadStats()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

// 选择变化
const handleRegionSelectionChange = (selection) => {
  selectedRegions.value = selection
}

const handleDataSelectionChange = (selection) => {
  selectedData.value = selection
}

const handleUploadedFileSelectionChange = (selection) => {
  selectedUploadedFiles.value = selection
}

// 格式化大小
const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(2) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(2) + ' GB'
}

// ============ 已上传文件管理 ============

// 加载上传文件统计
const loadUploadStats = async () => {
  try {
    const res = await getUploadStats()
    uploadStats.value = res
  } catch (err) {
    console.error('加载上传统计失败:', err)
  }
}

// 加载已上传文件列表
const loadUploadedFiles = async () => {
  loadingUploadedFiles.value = true
  try {
    const res = await getUploadedFiles()
    uploadedFiles.value = res.files || []
    loadUploadStats()
  } catch (err) {
    ElMessage.error('加载已上传文件列表失败')
  } finally {
    loadingUploadedFiles.value = false
  }
}

// 搜索过滤
const filterUploadedFiles = () => {
  // 搜索由 computed 自动处理
}

// 查看文件详情
const viewUploadedFileDetail = async (row) => {
  try {
    const res = await getUploadedFileInfo(row.filename)
    currentUploadedFile.value = res
    uploadedFileDetailVisible.value = true
  } catch (err) {
    ElMessage.error('加载文件详情失败')
  }
}

// 删除文件
const deleteUploadedFile = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${row.filename}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await apiDeleteUploadedFile(row.filename)
    ElMessage.success('删除成功')
    loadUploadedFiles()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除失败')
    }
  }
}

// 从对话框删除文件
const deleteUploadedFileFromDialog = async () => {
  if (!currentUploadedFile.value) return
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${currentUploadedFile.value.filename}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await apiDeleteUploadedFile(currentUploadedFile.value.filename)
    ElMessage.success('删除成功')
    uploadedFileDetailVisible.value = false
    loadUploadedFiles()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '删除失败')
    }
  }
}

// 批量删除文件
const batchDeleteUploadedFiles = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedUploadedFiles.value.length} 个文件吗？`, '确认删除', {
      type: 'warning'
    })
    const filenames = selectedUploadedFiles.value.map(f => f.filename)
    const res = await deleteMultipleFiles(filenames)
    if (res.success) {
      ElMessage.success(`成功删除 ${res.deleted_count} 个文件`)
    } else {
      ElMessage.warning(`成功 ${res.deleted_count} 个，失败 ${res.failed_count} 个`)
    }
    loadUploadedFiles()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '批量删除失败')
    }
  }
}

onMounted(() => {
  loadStats()
  loadRegions()
  loadAllRegions()
  loadProjectData()
  loadUploadedFiles()
  loadUploadStats()
})
</script>

<style scoped>
.data-manage-container {
  padding: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}

.tab-toolbar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.upload-summary {
  margin-top: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.columns-list {
  max-height: 150px;
  overflow-y: auto;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>
