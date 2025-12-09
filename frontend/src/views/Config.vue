<template>
  <div class="config-page">
    <!-- 当前选择信息 -->
    <div v-if="store.hasSelection" class="current-selection">
      <el-tag>{{ getCategoryName() }}</el-tag>
      <el-icon><ArrowRight /></el-icon>
      <el-tag type="success">{{ getTopicName() }}</el-tag>
      <el-icon><ArrowRight /></el-icon>
      <el-tag type="warning">{{ store.selectedRegion?.name }}</el-tag>
    </div>

    <!-- 无选择时提示 -->
    <el-alert
      v-if="!store.hasSelection"
      title="请先选择专题和地区"
      description="请返回首页选择大类、专题和地区后再进行配置"
      type="warning"
      show-icon
      :closable="false"
    >
      <template #default>
        <el-button type="primary" size="small" @click="$router.push('/')">
          返回首页
        </el-button>
      </template>
    </el-alert>

    <!-- 配置内容 -->
    <template v-if="store.hasSelection">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载配置中...</span>
      </div>

      <template v-else>
        <!-- 基础配置 -->
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>基础配置</span>
            </div>
          </template>

          <el-form label-width="120px">
            <el-form-item label="区域名称">
              <el-input :value="store.selectedRegion?.name" disabled>
                <template #prefix>
                  <el-icon><Location /></el-icon>
                </template>
              </el-input>
              <div class="form-tip">区域名称由已选择的项目决定</div>
            </el-form-item>

            <el-form-item label="普查年份">
              <el-date-picker
                v-model="surveyYear"
                type="year"
                placeholder="选择年份"
                value-format="YYYY"
              />
            </el-form-item>

            <el-form-item label="历史对比年份">
              <el-date-picker
                v-model="historicalYear"
                type="year"
                placeholder="选择年份（可选）"
                value-format="YYYY"
                clearable
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 分级标准配置 - 仅属性图专题显示 -->
        <el-card v-if="showGradingConfig" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>分级标准配置</span>
              <el-tag size="small" type="info">{{ getTopicName() }}专用</el-tag>
            </div>
          </template>

          <el-form label-width="120px">
            <el-form-item label="分级标准">
              <el-select
                v-model="currentStandard"
                placeholder="选择分级标准"
                :loading="loadingStandards"
                @change="handleStandardChange"
                style="width: 300px"
              >
                <el-option
                  v-for="std in gradingStandards"
                  :key="std.id"
                  :label="std.name"
                  :value="std.id"
                >
                  <div class="standard-option">
                    <span>{{ std.name }}</span>
                    <span class="description">{{ std.description }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>

          <!-- 属性配置表格 -->
          <div v-if="gradingAttributes.length > 0" class="attributes-section">
            <div class="section-title">
              <span>属性分级详情</span>
              <el-tag size="small" type="info">共 {{ gradingAttributes.length }} 个属性</el-tag>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索属性..."
                size="small"
                style="width: 200px; margin-left: auto"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <el-table
              :data="filteredAttributes"
              stripe
              border
              size="small"
              max-height="400"
            >
              <el-table-column prop="name" label="属性名称" width="140" fixed />
              <el-table-column prop="unit" label="单位" width="100" align="center">
                <template #default="{ row }">
                  <span>{{ row.unit || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column label="分级标准" min-width="400">
                <template #default="{ row }">
                  <div class="levels-display">
                    <el-tag
                      v-for="(level, idx) in row.levels"
                      :key="idx"
                      :type="getLevelTagType(level.level)"
                      size="small"
                      class="level-tag"
                    >
                      {{ level.level }}: {{ level.description }} (≤{{ level.threshold }})
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="land_filter" label="地类过滤" width="100" align="center">
                <template #default="{ row }">
                  <el-tooltip v-if="row.land_filter" :content="getLandFilterDesc(row.land_filter)">
                    <el-tag size="small" type="warning">
                      {{ getLandFilterName(row.land_filter) }}
                    </el-tag>
                  </el-tooltip>
                  <span v-else class="no-filter">全部</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <el-empty v-else-if="!loadingAttributes" description="暂无属性配置" />
          <div v-else class="loading-placeholder">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
        </el-card>

        <!-- 属性图数据处理配置 -->
        <el-card v-if="isAttributeMapTopic" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataBoard /></el-icon>
              <span>数据处理配置</span>
              <el-tag size="small" type="info">属性图专用</el-tag>
            </div>
          </template>

          <el-form label-width="120px">
            <el-form-item label="面积字段">
              <el-input
                v-model="dataProcessConfig.area_column"
                placeholder="面积"
                style="width: 200px"
              />
              <div class="form-tip">数据中的面积列名称</div>
            </el-form-item>

            <el-form-item label="乡镇字段">
              <el-input
                v-model="dataProcessConfig.town_column"
                placeholder="XZQMC"
                style="width: 200px"
              />
              <div class="form-tip">数据中的乡镇列名称</div>
            </el-form-item>

            <el-form-item label="地类字段">
              <el-input
                v-model="dataProcessConfig.land_use_column"
                placeholder="TDLYLX"
                style="width: 200px"
              />
              <div class="form-tip">数据中的土地利用类型列名称</div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 属性图统计配置 -->
        <el-card v-if="isAttributeMapTopic" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><PieChart /></el-icon>
              <span>统计配置</span>
              <el-tag size="small" type="info">属性图专用</el-tag>
            </div>
          </template>

          <el-form label-width="140px">
            <el-form-item label="分乡镇统计">
              <el-switch v-model="statsConfig.include_town_stats" />
              <span class="switch-label">{{ statsConfig.include_town_stats ? '启用' : '禁用' }}</span>
            </el-form-item>

            <el-form-item label="分地类统计">
              <el-switch v-model="statsConfig.include_land_use_stats" />
              <span class="switch-label">{{ statsConfig.include_land_use_stats ? '启用' : '禁用' }}</span>
            </el-form-item>

            <el-form-item label="分土壤类型统计">
              <el-switch v-model="statsConfig.include_soil_type_stats" />
              <span class="switch-label">{{ statsConfig.include_soil_type_stats ? '启用' : '禁用' }}</span>
            </el-form-item>

            <el-form-item label="百分位数列表">
              <el-select
                v-model="statsConfig.percentile_list"
                multiple
                placeholder="选择百分位数"
                style="width: 400px"
              >
                <el-option
                  v-for="p in availablePercentiles"
                  :key="p"
                  :label="`${p}%`"
                  :value="p"
                />
              </el-select>
              <div class="form-tip">用于计算数据分布的百分位数</div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 属性图上图配置 -->
        <el-card v-if="isAttributeMapTopic" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><MapLocation /></el-icon>
              <span>上图配置</span>
              <el-tag size="small" type="info">属性图专用</el-tag>
            </div>
          </template>

          <el-form label-width="120px">
            <el-form-item label="配色方案">
              <el-select v-model="mappingConfig.color_scheme" style="width: 200px">
                <el-option label="默认配色" value="default" />
                <el-option label="暖色调" value="warm" />
                <el-option label="冷色调" value="cool" />
                <el-option label="高对比度" value="high_contrast" />
              </el-select>
            </el-form-item>

            <el-form-item label="图例位置">
              <el-select v-model="mappingConfig.legend_position" style="width: 200px">
                <el-option label="右下角" value="bottom_right" />
                <el-option label="左下角" value="bottom_left" />
                <el-option label="右上角" value="top_right" />
                <el-option label="左上角" value="top_left" />
              </el-select>
            </el-form-item>

            <el-form-item label="显示标注">
              <el-switch v-model="mappingConfig.show_labels" />
              <span class="switch-label">{{ mappingConfig.show_labels ? '显示' : '隐藏' }}</span>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 数据报告数据处理配置 -->
        <el-card v-if="isDataReportTopic" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataBoard /></el-icon>
              <span>数据处理配置</span>
              <el-tag size="small" type="info">数据报告专用</el-tag>
            </div>
          </template>

          <el-form label-width="120px">
            <el-form-item label="面积字段">
              <el-input
                v-model="dataReportDataConfig.area_column"
                placeholder="面积"
                style="width: 200px"
              />
              <div class="form-tip">数据中的面积列名称</div>
            </el-form-item>

            <el-form-item label="乡镇字段">
              <el-input
                v-model="dataReportDataConfig.town_column"
                placeholder="XZQMC"
                style="width: 200px"
              />
              <div class="form-tip">数据中的乡镇列名称</div>
            </el-form-item>

            <el-form-item label="地类字段">
              <el-input
                v-model="dataReportDataConfig.land_use_column"
                placeholder="TDLYLX"
                style="width: 200px"
              />
              <div class="form-tip">数据中的土地利用类型列名称</div>
            </el-form-item>

            <el-form-item label="土壤亚类字段">
              <el-input
                v-model="dataReportDataConfig.soil_type_column"
                placeholder="YL"
                style="width: 200px"
              />
              <div class="form-tip">数据中的土壤亚类列名称</div>
            </el-form-item>

            <el-form-item label="土属字段">
              <el-input
                v-model="dataReportDataConfig.soil_subtype_column"
                placeholder="TS"
                style="width: 200px"
              />
              <div class="form-tip">数据中的土属列名称</div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 数据报告统计配置 -->
        <el-card v-if="isDataReportTopic" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><PieChart /></el-icon>
              <span>统计配置</span>
              <el-tag size="small" type="info">数据报告专用</el-tag>
            </div>
          </template>

          <el-form label-width="140px">
            <el-form-item label="分乡镇统计">
              <el-switch v-model="dataReportStatsConfig.include_town_stats" />
              <span class="switch-label">{{ dataReportStatsConfig.include_town_stats ? '启用' : '禁用' }}</span>
            </el-form-item>

            <el-form-item label="分地类统计">
              <el-switch v-model="dataReportStatsConfig.include_land_use_stats" />
              <span class="switch-label">{{ dataReportStatsConfig.include_land_use_stats ? '启用' : '禁用' }}</span>
            </el-form-item>

            <el-form-item label="分土壤类型统计">
              <el-switch v-model="dataReportStatsConfig.include_soil_type_stats" />
              <span class="switch-label">{{ dataReportStatsConfig.include_soil_type_stats ? '启用' : '禁用' }}</span>
            </el-form-item>

            <el-form-item label="百分位数列表">
              <el-select
                v-model="dataReportStatsConfig.percentile_list"
                multiple
                placeholder="选择百分位数"
                style="width: 400px"
              >
                <el-option
                  v-for="p in availablePercentiles"
                  :key="p"
                  :label="`${p}%`"
                  :value="p"
                />
              </el-select>
              <div class="form-tip">用于计算数据分布的百分位数</div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 数据报告输出配置 -->
        <el-card v-if="isDataReportTopic" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>输出配置</span>
              <el-tag size="small" type="info">数据报告专用</el-tag>
            </div>
          </template>

          <el-form label-width="140px">
            <el-form-item label="输出格式">
              <el-select v-model="dataReportOutputConfig.output_format" style="width: 200px">
                <el-option label="Excel (.xlsx)" value="xlsx" />
                <el-option label="Excel 97-2003 (.xls)" value="xls" />
              </el-select>
            </el-form-item>

            <el-form-item label="包含汇总表">
              <el-switch v-model="dataReportOutputConfig.include_summary_sheet" />
              <span class="switch-label">{{ dataReportOutputConfig.include_summary_sheet ? '是' : '否' }}</span>
            </el-form-item>

            <el-form-item label="包含明细表">
              <el-switch v-model="dataReportOutputConfig.include_detail_sheets" />
              <span class="switch-label">{{ dataReportOutputConfig.include_detail_sheets ? '是' : '否' }}</span>
            </el-form-item>

            <el-form-item label="小数位数">
              <el-input-number
                v-model="dataReportOutputConfig.decimal_places"
                :min="0"
                :max="6"
                style="width: 200px"
              />
              <div class="form-tip">数值保留的小数位数</div>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 类型图配置 -->
        <el-card v-if="store.selectedTopic === 'type_map'" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Grid /></el-icon>
              <span>类型图配置</span>
              <el-tag size="small" type="info">类型图专用</el-tag>
            </div>
          </template>

          <el-alert
            title="类型图配置将在后续阶段实现"
            type="info"
            show-icon
            :closable="false"
          />
        </el-card>

        <!-- 适宜性评价配置 -->
        <el-card v-if="store.selectedTopic === 'suitability'" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>适宜性评价配置</span>
              <el-tag size="small" type="info">适宜性评价专用</el-tag>
            </div>
          </template>

          <el-alert
            title="适宜性评价配置将在后续阶段实现"
            type="info"
            show-icon
            :closable="false"
          />
        </el-card>

        <!-- 等级评价配置 -->
        <el-card v-if="store.selectedTopic === 'grade_eval'" class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>等级评价配置</span>
              <el-tag size="small" type="info">等级评价专用</el-tag>
            </div>
          </template>

          <el-alert
            title="等级评价配置将在后续阶段实现"
            type="info"
            show-icon
            :closable="false"
          />
        </el-card>
      </template>
    </template>

    <!-- 操作按钮 -->
    <div class="page-actions">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <el-button type="primary" @click="handleSave" :disabled="!store.hasSelection || saving">
        <el-icon v-if="saving" class="is-loading"><Loading /></el-icon>
        {{ saving ? '保存中...' : '保存配置' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  ArrowLeft,
  Loading,
  Setting,
  Location,
  DataLine,
  Grid,
  TrendCharts,
  DataAnalysis,
  Search,
  DataBoard,
  PieChart,
  MapLocation,
  Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import {
  getGradingStandards,
  getCurrentGradingAttributes,
  createOrGetTopicConfig,
  updateTopicBaseConfig,
  updateTopicGradingStandard,
  updateAttributeMapDataConfig,
  updateAttributeMapMappingConfig,
  updateAttributeMapStatsConfig,
  updateDataReportDataConfig,
  updateDataReportStatsConfig,
  updateDataReportOutputConfig
} from '@/api'

const router = useRouter()
const store = useProjectStore()

// 加载状态
const loading = ref(false)
const saving = ref(false)

// 当前专题配置
const topicConfig = ref(null)

// 分级标准相关
const gradingStandards = ref([])
const currentStandard = ref('')
const gradingAttributes = ref([])
const loadingStandards = ref(false)
const loadingAttributes = ref(false)
const searchKeyword = ref('')

// 数据处理配置
const dataProcessConfig = reactive({
  enabled_attributes: [],
  area_column: '面积',
  town_column: 'XZQMC',
  land_use_column: 'TDLYLX'
})

// 统计配置
const statsConfig = reactive({
  include_town_stats: true,
  include_land_use_stats: true,
  include_soil_type_stats: true,
  percentile_list: [2, 5, 10, 20, 80, 90, 95, 98]
})

// 上图配置
const mappingConfig = reactive({
  color_scheme: 'default',
  legend_position: 'bottom_right',
  show_labels: true
})

// 数据报告-数据处理配置
const dataReportDataConfig = reactive({
  enabled_attributes: [],
  area_column: '面积',
  town_column: 'XZQMC',
  land_use_column: 'TDLYLX',
  soil_type_column: 'YL',
  soil_subtype_column: 'TS'
})

// 数据报告-统计配置
const dataReportStatsConfig = reactive({
  include_town_stats: true,
  include_land_use_stats: true,
  include_soil_type_stats: true,
  percentile_list: [2, 5, 10, 20, 80, 90, 95, 98]
})

// 数据报告-输出配置
const dataReportOutputConfig = reactive({
  output_format: 'xlsx',
  include_summary_sheet: true,
  include_detail_sheets: true,
  decimal_places: 2
})

// 可用的百分位数选项
const availablePercentiles = [1, 2, 5, 10, 20, 25, 50, 75, 80, 90, 95, 98, 99]

// 专题名称映射
const categoryNames = {
  soil_survey: '土壤普查',
  land_quality: '耕地质量'
}

const topicNames = {
  attribute_map: '属性图',
  type_map: '类型图',
  suitability: '适宜性评价',
  grade_eval: '等级评价',
  data_report: '数据报告'
}

const getCategoryName = () => {
  return categoryNames[store.selectedCategory] || store.selectedCategory
}

const getTopicName = () => {
  return topicNames[store.selectedTopic] || store.selectedTopic
}

// 是否显示分级标准配置（属性图和数据报告专题）
const showGradingConfig = computed(() => {
  return store.selectedTopic === 'attribute_map' || store.selectedTopic === 'data_report'
})

// 是否是属性图专题
const isAttributeMapTopic = computed(() => {
  return store.selectedTopic === 'attribute_map'
})

// 是否是数据报告专题
const isDataReportTopic = computed(() => {
  return store.selectedTopic === 'data_report'
})

// 过滤后的属性列表
const filteredAttributes = computed(() => {
  if (!searchKeyword.value) {
    return gradingAttributes.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return gradingAttributes.value.filter(attr =>
    attr.name.toLowerCase().includes(keyword) ||
    attr.key.toLowerCase().includes(keyword)
  )
})

// 年份配置
const surveyYear = computed({
  get: () => topicConfig.value?.survey_year?.toString() || new Date().getFullYear().toString(),
  set: (val) => {
    if (topicConfig.value) {
      topicConfig.value.survey_year = val ? parseInt(val, 10) : new Date().getFullYear()
    }
  }
})

const historicalYear = computed({
  get: () => topicConfig.value?.historical_year?.toString() || '',
  set: (val) => {
    if (topicConfig.value) {
      topicConfig.value.historical_year = val ? parseInt(val, 10) : null
    }
  }
})

// 加载专题配置
const loadTopicConfig = async () => {
  if (!store.hasSelection) return

  loading.value = true
  try {
    const config = await createOrGetTopicConfig(
      store.selectedTopic,
      store.selectedRegion.id,
      store.selectedRegion.name
    )
    topicConfig.value = config

    // 如果是属性图专题，加载相关配置
    if (isAttributeMapTopic.value && config.attribute_map) {
      currentStandard.value = config.attribute_map.grading_standard || 'jiangsu'

      // 数据处理配置
      if (config.attribute_map.data_process) {
        Object.assign(dataProcessConfig, config.attribute_map.data_process)
      }

      // 统计配置
      if (config.attribute_map.stats) {
        Object.assign(statsConfig, config.attribute_map.stats)
      }

      // 上图配置
      if (config.attribute_map.mapping) {
        Object.assign(mappingConfig, config.attribute_map.mapping)
      }

      // 加载分级标准和属性
      await loadGradingStandards()
    }

    // 如果是数据报告专题，加载相关配置
    if (isDataReportTopic.value && config.data_report) {
      currentStandard.value = config.data_report.grading_standard || 'jiangsu'

      // 数据处理配置
      if (config.data_report.data_process) {
        Object.assign(dataReportDataConfig, config.data_report.data_process)
      }

      // 统计配置
      if (config.data_report.stats) {
        Object.assign(dataReportStatsConfig, config.data_report.stats)
      }

      // 输出配置
      if (config.data_report.output) {
        Object.assign(dataReportOutputConfig, config.data_report.output)
      }

      // 加载分级标准和属性
      await loadGradingStandards()
    }
  } catch (error) {
    console.error('加载专题配置失败:', error)
    ElMessage.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

// 加载分级标准列表
const loadGradingStandards = async () => {
  if (!showGradingConfig.value) return

  loadingStandards.value = true
  try {
    const standards = await getGradingStandards()
    gradingStandards.value = standards

    // 加载属性配置
    await loadGradingAttributes()
  } catch (error) {
    console.error('加载分级标准失败:', error)
    ElMessage.error('加载分级标准失败')
  } finally {
    loadingStandards.value = false
  }
}

// 加载属性配置
const loadGradingAttributes = async () => {
  loadingAttributes.value = true
  try {
    const result = await getCurrentGradingAttributes()
    gradingAttributes.value = result.attributes
  } catch (error) {
    console.error('加载属性配置失败:', error)
  } finally {
    loadingAttributes.value = false
  }
}

// 切换分级标准
const handleStandardChange = async (standardId) => {
  if (!store.hasSelection) return

  try {
    await updateTopicGradingStandard(
      store.selectedTopic,
      store.selectedRegion.id,
      standardId
    )
    ElMessage.success('分级标准已切换')
    await loadGradingAttributes()
  } catch (error) {
    ElMessage.error(error.message || '切换分级标准失败')
  }
}

// 获取级别标签类型
const getLevelTagType = (level) => {
  if (level.includes('1')) return 'success'
  if (level.includes('2')) return ''
  if (level.includes('3')) return 'info'
  if (level.includes('4')) return 'warning'
  return 'danger'
}

// 获取地类过滤名称
const getLandFilterName = (filter) => {
  const filterNames = {
    cultivated_garden: '耕园地',
    cultivated_only: '耕地',
    paddy_only: '水田'
  }
  return filterNames[filter] || filter
}

// 获取地类过滤描述
const getLandFilterDesc = (filter) => {
  const filterDescs = {
    cultivated_garden: '仅统计耕地和园地',
    cultivated_only: '仅统计耕地（水田、水浇地、旱地）',
    paddy_only: '仅统计水田'
  }
  return filterDescs[filter] || filter
}

const goBack = () => {
  router.push('/')
}

const handleSave = async () => {
  if (!store.hasSelection) return

  saving.value = true
  try {
    const topic = store.selectedTopic
    const regionId = store.selectedRegion.id

    // 保存基础配置
    await updateTopicBaseConfig(topic, regionId, {
      survey_year: topicConfig.value?.survey_year || new Date().getFullYear(),
      historical_year: topicConfig.value?.historical_year || null
    })

    // 如果是属性图专题，保存专用配置
    if (isAttributeMapTopic.value) {
      // 保存数据处理配置
      await updateAttributeMapDataConfig(topic, regionId, {
        enabled_attributes: dataProcessConfig.enabled_attributes,
        area_column: dataProcessConfig.area_column,
        town_column: dataProcessConfig.town_column,
        land_use_column: dataProcessConfig.land_use_column
      })

      // 保存统计配置
      await updateAttributeMapStatsConfig(topic, regionId, {
        include_town_stats: statsConfig.include_town_stats,
        include_land_use_stats: statsConfig.include_land_use_stats,
        include_soil_type_stats: statsConfig.include_soil_type_stats,
        percentile_list: statsConfig.percentile_list
      })

      // 保存上图配置
      await updateAttributeMapMappingConfig(topic, regionId, {
        color_scheme: mappingConfig.color_scheme,
        legend_position: mappingConfig.legend_position,
        show_labels: mappingConfig.show_labels
      })
    }

    // 如果是数据报告专题，保存专用配置
    if (isDataReportTopic.value) {
      // 保存数据处理配置
      await updateDataReportDataConfig(topic, regionId, {
        enabled_attributes: dataReportDataConfig.enabled_attributes,
        area_column: dataReportDataConfig.area_column,
        town_column: dataReportDataConfig.town_column,
        land_use_column: dataReportDataConfig.land_use_column,
        soil_type_column: dataReportDataConfig.soil_type_column,
        soil_subtype_column: dataReportDataConfig.soil_subtype_column
      })

      // 保存统计配置
      await updateDataReportStatsConfig(topic, regionId, {
        include_town_stats: dataReportStatsConfig.include_town_stats,
        include_land_use_stats: dataReportStatsConfig.include_land_use_stats,
        include_soil_type_stats: dataReportStatsConfig.include_soil_type_stats,
        percentile_list: dataReportStatsConfig.percentile_list
      })

      // 保存输出配置
      await updateDataReportOutputConfig(topic, regionId, {
        output_format: dataReportOutputConfig.output_format,
        include_summary_sheet: dataReportOutputConfig.include_summary_sheet,
        include_detail_sheets: dataReportOutputConfig.include_detail_sheets,
        decimal_places: dataReportOutputConfig.decimal_places
      })
    }

    ElMessage.success('配置保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 监听专题/地区变化，重新加载配置
watch(
  () => [store.selectedTopic, store.selectedRegion?.id],
  () => {
    if (store.hasSelection) {
      loadTopicConfig()
    }
  }
)

onMounted(() => {
  if (store.hasSelection) {
    loadTopicConfig()
  }
})
</script>

<style scoped>
.config-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.current-selection {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.current-selection .el-icon {
  color: #909399;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 60px;
  color: #909399;
  font-size: 16px;
}

.config-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: bold;
}

.card-header .el-icon {
  color: var(--el-color-primary);
}

.card-header .el-tag {
  margin-left: auto;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.standard-option {
  display: flex;
  flex-direction: column;
}

.standard-option .description {
  font-size: 12px;
  color: #909399;
}

.attributes-section {
  margin-top: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-weight: bold;
}

.levels-display {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.level-tag {
  margin: 2px 0;
}

.no-filter {
  color: #909399;
  font-size: 12px;
}

.loading-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: #909399;
}

.switch-label {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

.page-actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
}
</style>
