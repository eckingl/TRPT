<template>
  <div class="home">
    <!-- 标题 -->
    <div class="header">
      <h1>农业土壤普查报告生成系统</h1>
      <p class="subtitle">请依次选择大类、专题和地区</p>
    </div>

    <!-- 层级选择区域 -->
    <div class="selection-area">
      <!-- 第一级：大类选择 -->
      <div class="level-section">
        <div class="level-title">
          <span class="level-number">1</span>
          <span>选择大类</span>
        </div>
        <div class="card-grid">
          <div
            v-for="category in categories"
            :key="category.id"
            class="selection-card"
            :class="{ active: selectedCategory === category.id }"
            @click="selectCategory(category.id)"
          >
            <el-icon :size="32"><component :is="category.icon" /></el-icon>
            <span class="card-title">{{ category.name }}</span>
            <span class="card-desc">{{ category.description }}</span>
          </div>
        </div>
      </div>

      <!-- 第二级：专题选择 -->
      <div v-if="selectedCategory" class="level-section">
        <div class="level-title">
          <span class="level-number">2</span>
          <span>选择专题</span>
        </div>
        <div class="card-grid">
          <div
            v-for="topic in currentTopics"
            :key="topic.id"
            class="selection-card"
            :class="{ active: selectedTopic === topic.id }"
            @click="selectTopic(topic.id)"
          >
            <el-icon :size="28"><component :is="topic.icon" /></el-icon>
            <span class="card-title">{{ topic.name }}</span>
            <span class="card-desc">{{ topic.description }}</span>
          </div>
        </div>
      </div>

      <!-- 第三级：地区选择/新建 -->
      <div v-if="selectedTopic" class="level-section">
        <div class="level-title">
          <span class="level-number">3</span>
          <span>选择或新建地区</span>
          <el-button type="primary" size="small" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建地区
          </el-button>
        </div>

        <!-- 已有地区列表 -->
        <div v-if="regions.length > 0" class="region-list">
          <div
            v-for="region in regions"
            :key="region.id"
            class="region-card"
            :class="{ active: selectedRegion?.id === region.id }"
            @click="selectRegion(region)"
          >
            <div class="region-info">
              <span class="region-name">{{ region.name }}</span>
              <span class="region-time">更新于 {{ formatTime(region.updated_at) }}</span>
            </div>
            <div class="region-actions" @click.stop>
              <el-button text type="danger" size="small" @click="handleDeleteRegion(region)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 无地区提示 -->
        <div v-else class="empty-regions">
          <el-empty description="暂无地区，请新建">
            <el-button type="primary" @click="showCreateDialog = true">
              <el-icon><Plus /></el-icon>
              新建地区
            </el-button>
          </el-empty>
        </div>
      </div>

      <!-- 第四级：具体操作 -->
      <div v-if="selectedRegion" class="level-section">
        <div class="level-title">
          <span class="level-number">4</span>
          <span>选择操作</span>
        </div>
        <div class="card-grid">
          <div
            v-for="action in actions"
            :key="action.id"
            class="selection-card action-card"
            @click="handleAction(action.id)"
          >
            <el-icon :size="28"><component :is="action.icon" /></el-icon>
            <span class="card-title">{{ action.name }}</span>
            <span class="card-desc">{{ action.description }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 当前选择摘要 -->
    <div v-if="selectedCategory" class="selection-summary-bar">
      <div class="summary-content">
        <el-tag>{{ getCategoryName() }}</el-tag>
        <template v-if="selectedTopic">
          <el-icon><ArrowRight /></el-icon>
          <el-tag type="success">{{ getTopicName() }}</el-tag>
        </template>
        <template v-if="selectedRegion">
          <el-icon><ArrowRight /></el-icon>
          <el-tag type="warning">{{ selectedRegion.name }}</el-tag>
        </template>
      </div>
    </div>

    <!-- 系统状态 -->
    <div class="status-bar">
      <span>系统状态：</span>
      <el-tag :type="healthStatus === 'ok' ? 'success' : 'danger'" size="small">
        {{ healthStatus === 'ok' ? '正常' : '连接中...' }}
      </el-tag>
      <span class="version">v{{ version }}</span>
    </div>

    <!-- 新建地区对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建地区" width="400px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="地区名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入地区名称，如：XX县" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateRegion">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  Document,
  DataAnalysis,
  PictureFilled,
  Grid,
  ArrowRight,
  TrendCharts,
  Plus,
  Delete,
  Upload,
  Setting,
  Document as DocIcon,
  View
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { checkHealth, getRegions, createRegion, deleteRegion } from '@/api'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const store = useProjectStore()

const healthStatus = ref('checking')
const version = ref('-')

const selectedCategory = ref(null)
const selectedTopic = ref(null)
const selectedRegion = ref(null)
const regions = ref([])
const loadingRegions = ref(false)

// 新建地区
const showCreateDialog = ref(false)
const creating = ref(false)
const createFormRef = ref()
const createForm = ref({ name: '' })
const createRules = {
  name: [{ required: true, message: '请输入地区名称', trigger: 'blur' }]
}

// 大类数据
const categories = [
  {
    id: 'soil_survey',
    name: '土壤普查',
    description: '第三次全国土壤普查',
    icon: Document
  },
  {
    id: 'land_quality',
    name: '耕地质量',
    description: '耕地质量等级评价',
    icon: DataAnalysis
  }
]

// 专题数据
const topics = {
  soil_survey: [
    {
      id: 'attribute_map',
      name: '属性图',
      description: '土壤属性专题图',
      icon: PictureFilled
    },
    {
      id: 'type_map',
      name: '类型图',
      description: '土壤类型分布图',
      icon: Grid
    },
    {
      id: 'suitability',
      name: '适宜性评价',
      description: '作物适宜性分析',
      icon: TrendCharts
    }
  ],
  land_quality: [
    {
      id: 'grade_eval',
      name: '等级评价',
      description: '耕地质量等级',
      icon: DataAnalysis
    }
  ]
}

// 操作列表
const actions = [
  {
    id: 'upload',
    name: '上传数据',
    description: '上传或更新数据文件',
    icon: Upload
  },
  {
    id: 'config',
    name: '配置参数',
    description: '设置分级标准等参数',
    icon: Setting
  },
  {
    id: 'preview',
    name: '预览数据',
    description: '查看已上传的数据',
    icon: View
  },
  {
    id: 'generate',
    name: '生成报告',
    description: '生成Word报告文档',
    icon: DocIcon
  }
]

// 计算当前可选的专题
const currentTopics = computed(() => {
  return selectedCategory.value ? topics[selectedCategory.value] || [] : []
})

// 选择大类
const selectCategory = (id) => {
  selectedCategory.value = id
  selectedTopic.value = null
  selectedRegion.value = null
  regions.value = []
}

// 选择专题
const selectTopic = async (id) => {
  selectedTopic.value = id
  selectedRegion.value = null
  await loadRegions()
}

// 加载地区列表
const loadRegions = async () => {
  if (!selectedCategory.value || !selectedTopic.value) return

  loadingRegions.value = true
  try {
    const data = await getRegions({
      category: selectedCategory.value,
      topic: selectedTopic.value
    })
    regions.value = data.regions || []
  } catch (error) {
    console.error('加载地区失败:', error)
    regions.value = []
  } finally {
    loadingRegions.value = false
  }
}

// 选择地区
const selectRegion = (region) => {
  selectedRegion.value = region
  // 保存到 store
  store.config.category = selectedCategory.value
  store.config.topic = selectedTopic.value
  store.config.regionId = region.id
  store.config.regionName = region.name
}

// 创建地区
const handleCreateRegion = async () => {
  try {
    await createFormRef.value?.validate()
  } catch {
    return
  }

  creating.value = true
  try {
    const newRegion = await createRegion({
      name: createForm.value.name,
      category: selectedCategory.value,
      topic: selectedTopic.value,
      item: selectedTopic.value // 暂时用 topic 作为 item
    })
    ElMessage.success('地区创建成功')
    showCreateDialog.value = false
    createForm.value.name = ''
    await loadRegions()
    // 自动选中新创建的地区
    selectRegion(newRegion)
  } catch (error) {
    ElMessage.error(error.message || '创建失败')
  } finally {
    creating.value = false
  }
}

// 删除地区
const handleDeleteRegion = async (region) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除地区"${region.name}"吗？该操作将删除所有相关数据，且不可恢复。`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteRegion(region.id)
    ElMessage.success('删除成功')
    if (selectedRegion.value?.id === region.id) {
      selectedRegion.value = null
    }
    await loadRegions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 处理操作
const handleAction = (actionId) => {
  switch (actionId) {
    case 'upload':
      router.push('/upload')
      break
    case 'config':
      router.push('/config')
      break
    case 'preview':
      ElMessage.info('数据预览功能将在后续阶段实现')
      break
    case 'generate':
      router.push('/report')
      break
  }
}

// 获取名称的辅助函数
const getCategoryName = () => {
  return categories.find(c => c.id === selectedCategory.value)?.name || ''
}

const getTopicName = () => {
  const topicList = topics[selectedCategory.value] || []
  return topicList.find(t => t.id === selectedTopic.value)?.name || ''
}

// 格式化时间
const formatTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(async () => {
  try {
    const data = await checkHealth()
    healthStatus.value = data.status
    version.value = data.version
  } catch {
    healthStatus.value = 'error'
  }
})
</script>

<style scoped>
.home {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  margin: 0 0 10px;
  font-size: 28px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 16px;
  margin: 0;
}

/* 层级选择区域 */
.selection-area {
  margin-bottom: 30px;
}

.level-section {
  margin-bottom: 30px;
}

.level-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.level-number {
  width: 24px;
  height: 24px;
  background: var(--el-color-primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

/* 卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

/* 选择卡片 */
.selection-card {
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.selection-card:hover {
  border-color: var(--el-color-primary-light-3);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.selection-card.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.selection-card .el-icon {
  color: var(--el-color-primary);
}

.action-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
}

.action-card:hover {
  background: linear-gradient(135deg, #ecf5ff 0%, #fff 100%);
}

.card-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.card-desc {
  font-size: 12px;
  color: #909399;
}

/* 地区列表 */
.region-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.region-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.region-card:hover {
  border-color: var(--el-color-primary-light-3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.region-card.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.region-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.region-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.region-time {
  font-size: 12px;
  color: #909399;
}

.empty-regions {
  padding: 40px 0;
  background: #fafafa;
  border-radius: 8px;
}

/* 选择摘要栏 */
.selection-summary-bar {
  position: sticky;
  bottom: 80px;
  background: #fff;
  border-radius: 8px;
  padding: 15px 20px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.summary-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.summary-content .el-icon {
  color: #909399;
}

/* 状态栏 */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  font-size: 14px;
  color: #606266;
}

.version {
  color: #909399;
}
</style>
