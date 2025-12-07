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
            <el-button
              type="primary"
              text
              class="history-btn"
              @click="openHistoryFileDialog('sample')"
            >
              <el-icon><FolderOpened /></el-icon>
              选择已有文件
            </el-button>
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
            <el-button
              type="primary"
              text
              class="history-btn"
              @click="openHistoryFileDialog('area')"
            >
              <el-icon><FolderOpened /></el-icon>
              选择已有文件
            </el-button>
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
            <el-button
              type="primary"
              text
              class="history-btn"
              @click="openHistoryFileDialog('mapping')"
            >
              <el-icon><FolderOpened /></el-icon>
              选择已有文件
            </el-button>
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
          <el-tag v-if="processResult.success" type="success">成功</el-tag>
          <el-tag v-else type="danger">失败</el-tag>
        </div>
      </template>

      <div v-if="!processResult.success" class="error-message">
        <el-alert :title="processResult.message" type="error" show-icon :closable="false" />
      </div>

      <div v-else>
        <!-- 下载Excel按钮 -->
        <div class="action-bar">
          <el-button type="success" @click="downloadResult">
            <el-icon><Download /></el-icon>
            下载 Excel 统计表
          </el-button>
          <el-button @click="clearResult">
            重新处理
          </el-button>
        </div>

        <!-- 数据预览 -->
        <div v-if="processResult.preview && processResult.preview.length > 0" class="preview-section">
          <h3>数据预览</h3>
          <el-table :data="processResult.preview" stripe border>
            <el-table-column prop="name" label="属性名称" width="140" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="sample_count" label="样点数" width="80" />
            <el-table-column label="均值" width="100">
              <template #default="{ row }">
                {{ row.sample_mean }} {{ row.unit }}
              </template>
            </el-table-column>
            <el-table-column label="范围" width="150">
              <template #default="{ row }">
                {{ row.sample_min }} ~ {{ row.sample_max }}
              </template>
            </el-table-column>
            <el-table-column label="等级分布" min-width="200">
              <template #default="{ row }">
                <div class="grade-distribution">
                  <span
                    v-for="(pct, grade) in row.grade_distribution"
                    :key="grade"
                    class="grade-item"
                  >
                    {{ grade }}: {{ pct }}%
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="选择" width="60" v-if="showReportForm">
              <template #default="{ row }">
                <el-checkbox
                  v-model="selectedAttributes"
                  :value="row.key"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 报告生成配置 -->
        <div class="report-section">
          <div class="section-header" @click="showReportForm = !showReportForm">
            <h3>
              <el-icon><Document /></el-icon>
              生成 Word 分析报告
            </h3>
            <el-icon>
              <ArrowDown v-if="!showReportForm" />
              <ArrowUp v-else />
            </el-icon>
          </div>

          <el-collapse-transition>
            <div v-show="showReportForm" class="report-form">
              <el-form :model="reportConfig" label-width="100px">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="选择地区" required>
                      <el-select
                        v-model="reportConfig.region_id"
                        style="width: 100%"
                        placeholder="请选择地区"
                        filterable
                        @change="onRegionChange"
                      >
                        <el-option
                          v-for="region in regions"
                          :key="region.id"
                          :label="region.name"
                          :value="region.id"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="调查年份">
                      <el-input-number v-model="reportConfig.survey_year" :min="2000" :max="2030" />
                    </el-form-item>
                  </el-col>
                </el-row>
                <el-row v-if="!reportConfig.region_id" :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="或输入地区">
                      <el-input v-model="reportConfig.region_name" placeholder="如：濮阳县（未选择地区时使用）" />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="报告模式">
                      <el-select v-model="reportConfig.report_mode" style="width: 100%" @change="onReportModeChange">
                        <el-option label="综合报告（所有属性）" value="multi" />
                        <el-option label="单属性报告" value="single" />
                        <el-option label="两者都生成" value="both" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="图表主题">
                      <el-select v-model="reportConfig.theme" style="width: 100%">
                        <el-option label="专业蓝" value="professional" />
                        <el-option label="大地色" value="earth" />
                        <el-option label="活力橙" value="vibrant" />
                        <el-option label="默认" value="default" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <!-- 单属性模式下选择具体属性（支持多选，按顺序生成） -->
                <el-row v-if="reportConfig.report_mode === 'single'" :gutter="20">
                  <el-col :span="24">
                    <el-form-item label="选择属性" required>
                      <div class="select-actions">
                        <el-button type="primary" link @click="selectAllAttributes">
                          <el-icon><Select /></el-icon>
                          全选
                        </el-button>
                        <el-button type="info" link @click="clearAllAttributes">
                          <el-icon><Close /></el-icon>
                          清空
                        </el-button>
                      </div>
                      <el-select
                        v-model="selectedSingleAttributes"
                        style="width: 100%"
                        placeholder="请选择要生成报告的属性（可多选，按顺序生成）"
                        multiple
                        collapse-tags
                        collapse-tags-tooltip
                      >
                        <el-option
                          v-for="attr in currentPreviewList"
                          :key="attr.key"
                          :label="`${attr.name} (${attr.unit}) - 均值: ${attr.sample_mean}`"
                          :value="attr.key"
                        />
                      </el-select>
                      <div class="select-hint">
                        <span v-if="selectedSingleAttributes.length > 0">
                          已选 {{ selectedSingleAttributes.length }}/{{ currentPreviewList.length }} 个属性，将按顺序生成 {{ selectedSingleAttributes.length }} 份报告
                        </span>
                        <span v-else>支持多选，每个属性将单独生成一份报告</span>
                      </div>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-form-item label="AI 分析">
                      <el-switch v-model="reportConfig.use_ai" />
                      <span v-if="reportConfig.use_ai" class="ai-hint">将调用 AI 生成专业分析文字</span>
                    </el-form-item>
                  </el-col>
                  <el-col :span="12" v-if="reportConfig.use_ai">
                    <el-form-item label="AI 提供商">
                      <el-select v-model="reportConfig.ai_provider" style="width: 100%">
                        <el-option label="DeepSeek" value="deepseek" />
                        <el-option label="通义千问" value="qwen" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-form-item>
                  <el-button
                    type="primary"
                    size="large"
                    :loading="generatingReport"
                    :disabled="generatingReport"
                    @click="generateWordReport"
                  >
                    <el-icon><Document /></el-icon>
                    {{ generatingReport ? '生成中...' : '生成 Word 报告' }}
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-collapse-transition>
        </div>

        <!-- 生成进度条 -->
        <div v-if="generatingReport && generateProgress.total > 0" class="progress-section">
          <div class="progress-header">
            <span class="progress-title">正在生成报告...</span>
            <span class="progress-count">{{ generateProgress.current }}/{{ generateProgress.total }}</span>
          </div>
          <el-progress
            :percentage="Math.round((generateProgress.current / generateProgress.total) * 100)"
            :status="generateProgress.currentError ? 'exception' : ''"
            :stroke-width="20"
            striped
            striped-flow
          />
          <div class="progress-current">
            <el-icon class="is-loading" v-if="!generateProgress.currentError"><Loading /></el-icon>
            <span>{{ generateProgress.currentAttr }}</span>
          </div>
        </div>

        <!-- 报告生成结果 -->
        <div v-if="reportResult" class="report-result">
          <!-- 成功结果 -->
          <el-result
            v-if="reportResult.success"
            icon="success"
            :title="`报告生成完成`"
            :sub-title="reportResult.message"
          >
            <template #extra>
              <div class="result-stats">
                <el-tag type="success" size="large">
                  成功: {{ reportResult.successCount }} 份
                </el-tag>
                <el-tag v-if="reportResult.failedCount > 0" type="danger" size="large">
                  失败: {{ reportResult.failedCount }} 份
                </el-tag>
              </div>

              <!-- 生成的文件列表 -->
              <div v-if="reportResult.generatedFiles && reportResult.generatedFiles.length > 0" class="generated-files">
                <div class="files-header">
                  <span>已生成 {{ reportResult.generatedFiles.length }} 份报告：</span>
                  <el-button type="primary" size="small" @click="downloadAllReports">
                    <el-icon><Download /></el-icon>
                    批量下载全部
                  </el-button>
                </div>
                <div class="files-list">
                  <div v-for="(file, index) in reportResult.generatedFiles" :key="index" class="file-item-download">
                    <el-icon><Document /></el-icon>
                    <span class="file-name">{{ file.attrName }}</span>
                    <el-button type="primary" link size="small" @click="downloadFile(file.url)">
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                  </div>
                </div>
              </div>

              <!-- 失败列表 -->
              <div v-if="reportResult.failedList && reportResult.failedList.length > 0" class="failed-list">
                <el-collapse>
                  <el-collapse-item title="查看失败详情" name="1">
                    <div v-for="(fail, index) in reportResult.failedList" :key="index" class="failed-item">
                      <el-tag type="danger" size="small">{{ fail.attrName }}</el-tag>
                      <span class="error-msg">{{ fail.error }}</span>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </template>
          </el-result>

          <!-- 全部失败 -->
          <el-result
            v-else
            icon="error"
            title="报告生成失败"
            :sub-title="reportResult.message"
          >
            <template #extra>
              <div v-if="reportResult.failedList && reportResult.failedList.length > 0" class="failed-list">
                <div v-for="(fail, index) in reportResult.failedList" :key="index" class="failed-item">
                  <el-tag type="danger" size="small">{{ fail.attrName }}</el-tag>
                  <span class="error-msg">{{ fail.error }}</span>
                </div>
              </div>
            </template>
          </el-result>
        </div>
      </div>
    </el-card>

    <!-- 历史处理记录 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>历史处理记录</span>
          <el-button text @click="refreshProcessRecords">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div v-if="processRecords.length > 0" class="history-list">
        <el-table :data="processRecords" stripe>
          <el-table-column label="处理时间" width="170">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="数据文件" min-width="180">
            <template #default="{ row }">
              <div class="file-names">
                <span v-for="f in row.sample_files.slice(0, 2)" :key="f" class="file-tag">{{ f }}</span>
                <span v-if="row.sample_files.length > 2" class="more-tag">+{{ row.sample_files.length - 2 }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="属性数量" width="90">
            <template #default="{ row }">
              {{ row.preview?.length || 0 }} 个
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="selectProcessRecord(row)">
                <el-icon><Document /></el-icon>
                生成报告
              </el-button>
              <el-button type="success" link @click="downloadFile(`/api/report/download/${encodeURIComponent(row.excel_filename)}`)">
                <el-icon><Download /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="暂无处理记录" />
    </el-card>

    <!-- 文件下载历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>文件下载</span>
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
      <el-empty v-else description="暂无文件" />
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
          :data="historyFiles"
          stripe
          max-height="400px"
          @selection-change="(rows) => selectedHistoryFiles = rows.map(r => r.filename)"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
          <el-table-column label="行数" width="80">
            <template #default="{ row }">
              {{ row.rows || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
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
  DataAnalysis,
  MapLocation,
  Document,
  QuestionFilled,
  UploadFilled,
  Delete,
  VideoPlay,
  Download,
  Refresh,
  ArrowLeft,
  ArrowDown,
  ArrowUp,
  FolderOpened,
  Select,
  Close,
  Loading
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  uploadFile as apiUploadFile,
  processAttributeData as apiProcessAttributeData,
  processMappingData as apiProcessMappingData,
  getReportList,
  generateReportFromProcess,
  getProcessRecords,
  getRegions,
  getUploadedFiles,
  getUploadedFileInfo
} from '@/api'

const currentFunction = ref('attribute')
const processing = ref(false)
const processResult = ref(null)
const reportList = ref([])

// 地区列表
const regions = ref([])

// 历史处理记录
const processRecords = ref([])

// 报告生成相关
const showReportForm = ref(false)
const generatingReport = ref(false)
const reportResult = ref(null)
const selectedAttributes = ref([])
const selectedSingleAttributes = ref([])  // 单属性模式下选中的属性列表（支持多选）
const reportConfig = ref({
  region_id: null,
  region_name: '',
  survey_year: 2024,
  report_mode: 'multi',
  theme: 'professional',
  use_ai: false,
  ai_provider: 'deepseek'
})

// 生成进度
const generateProgress = ref({
  current: 0,
  total: 0,
  currentAttr: '',
  currentError: false
})

// 当前预览数据列表（用于单属性选择）
const currentPreviewList = computed(() => {
  return processResult.value?.preview || []
})

// 全选属性
const selectAllAttributes = () => {
  selectedSingleAttributes.value = currentPreviewList.value.map(attr => attr.key)
}

// 清空选择
const clearAllAttributes = () => {
  selectedSingleAttributes.value = []
}

// 属性图数据处理的文件
const sampleFiles = ref([])
const areaFiles = ref([])
const uploadedSampleFiles = ref([])
const uploadedAreaFiles = ref([])

// 属性图上图处理的文件
const mappingFiles = ref([])
const uploadedMappingFiles = ref([])

// 历史文件选择对话框
const showHistoryFileDialog = ref(false)
const historyFiles = ref([])
const loadingHistoryFiles = ref(false)
const selectedHistoryFiles = ref([])
const historyFileTarget = ref('')  // 'sample' | 'area' | 'mapping'

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

// 打开历史文件选择对话框
const openHistoryFileDialog = async (target) => {
  historyFileTarget.value = target
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

// 确认选择历史文件
const confirmSelectHistoryFiles = async () => {
  if (selectedHistoryFiles.value.length === 0) {
    ElMessage.warning('请至少选择一个文件')
    return
  }

  // 获取选中文件的详细信息
  for (const filename of selectedHistoryFiles.value) {
    try {
      const fileInfo = await getUploadedFileInfo(filename)

      // 检查是否已存在
      const targetList = getTargetFileList()
      const exists = targetList.some(f => f.file_path === fileInfo.file_path)
      if (exists) {
        ElMessage.warning(`文件 ${filename} 已添加`)
        continue
      }

      // 添加到对应的文件列表
      if (historyFileTarget.value === 'sample') {
        uploadedSampleFiles.value.push(fileInfo)
      } else if (historyFileTarget.value === 'area') {
        uploadedAreaFiles.value.push(fileInfo)
      } else if (historyFileTarget.value === 'mapping') {
        uploadedMappingFiles.value.push(fileInfo)
      }
    } catch (error) {
      ElMessage.error(`获取文件 ${filename} 信息失败`)
    }
  }

  showHistoryFileDialog.value = false
  ElMessage.success(`已添加 ${selectedHistoryFiles.value.length} 个文件`)
}

// 获取目标文件列表
const getTargetFileList = () => {
  if (historyFileTarget.value === 'sample') {
    return uploadedSampleFiles.value
  } else if (historyFileTarget.value === 'area') {
    return uploadedAreaFiles.value
  } else if (historyFileTarget.value === 'mapping') {
    return uploadedMappingFiles.value
  }
  return []
}

// 格式化文件大小（用于历史文件列表）
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
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
  reportResult.value = null
  showReportForm.value = false
  selectedAttributes.value = []
}

// 生成 Word 报告
const generateWordReport = async () => {
  if (!processResult.value?.process_id) {
    ElMessage.warning('请先处理数据')
    return
  }

  // 必须选择地区或输入地区名称
  if (!reportConfig.value.region_id && !reportConfig.value.region_name) {
    ElMessage.warning('请选择地区或输入地区名称')
    return
  }

  // 单属性模式下必须选择至少一个属性
  if (reportConfig.value.report_mode === 'single' && selectedSingleAttributes.value.length === 0) {
    ElMessage.warning('请选择要生成报告的属性')
    return
  }

  generatingReport.value = true
  reportResult.value = null

  // 重置进度
  generateProgress.value = {
    current: 0,
    total: 0,
    currentAttr: '',
    currentError: false
  }

  try {
    // 确定地区名称
    let regionName = reportConfig.value.region_name
    if (reportConfig.value.region_id) {
      const region = regions.value.find(r => r.id === reportConfig.value.region_id)
      if (region) {
        regionName = region.name
      }
    }

    // 单属性模式：按顺序逐个生成报告
    if (reportConfig.value.report_mode === 'single' && selectedSingleAttributes.value.length > 0) {
      const totalCount = selectedSingleAttributes.value.length
      const generatedFiles = []  // 成功生成的文件列表
      const failedList = []  // 失败的属性列表

      // 设置进度总数
      generateProgress.value.total = totalCount

      for (let i = 0; i < totalCount; i++) {
        const attrKey = selectedSingleAttributes.value[i]
        const attrInfo = currentPreviewList.value.find(a => a.key === attrKey)
        const attrName = attrInfo?.name || attrKey

        // 更新进度
        generateProgress.value.current = i + 1
        generateProgress.value.currentAttr = `正在生成: ${attrName}`
        generateProgress.value.currentError = false

        const params = {
          process_id: processResult.value.process_id,
          region_name: regionName || 'XX县',
          survey_year: reportConfig.value.survey_year,
          theme: reportConfig.value.theme,
          report_mode: 'single',
          use_ai: reportConfig.value.use_ai,
          ai_provider: reportConfig.value.use_ai ? reportConfig.value.ai_provider : null,
          attributes: [attrKey]
        }

        try {
          const result = await generateReportFromProcess(params)
          if (result.success) {
            generatedFiles.push({
              attrKey,
              attrName,
              filename: result.filename,
              url: result.download_url
            })
          } else {
            generateProgress.value.currentError = true
            failedList.push({
              attrKey,
              attrName,
              error: result.message || '生成失败'
            })
          }
        } catch (err) {
          generateProgress.value.currentError = true
          failedList.push({
            attrKey,
            attrName,
            error: err.message || '请求超时或网络错误'
          })
          console.error(`生成 ${attrName} 报告失败:`, err)
        }
      }

      // 汇总结果
      const successCount = generatedFiles.length
      const failedCount = failedList.length

      if (successCount > 0) {
        reportResult.value = {
          success: true,
          message: failedCount > 0
            ? `成功生成 ${successCount} 份报告，${failedCount} 份失败`
            : `成功生成 ${successCount} 份报告`,
          successCount,
          failedCount,
          generatedFiles,
          failedList
        }
        ElMessage.success(`报告生成完成：成功 ${successCount} 份${failedCount > 0 ? `，失败 ${failedCount} 份` : ''}`)
        refreshHistory()
      } else {
        reportResult.value = {
          success: false,
          message: '所有报告生成失败',
          successCount: 0,
          failedCount,
          generatedFiles: [],
          failedList
        }
        ElMessage.error('所有报告生成失败')
      }
    } else {
      // 其他模式：一次性生成
      generateProgress.value.total = 1
      generateProgress.value.current = 1
      generateProgress.value.currentAttr = '正在生成综合报告...'

      let attributesToInclude = null
      if (selectedAttributes.value.length > 0) {
        attributesToInclude = selectedAttributes.value
      }

      const params = {
        process_id: processResult.value.process_id,
        region_name: regionName || 'XX县',
        survey_year: reportConfig.value.survey_year,
        theme: reportConfig.value.theme,
        report_mode: reportConfig.value.report_mode,
        use_ai: reportConfig.value.use_ai,
        ai_provider: reportConfig.value.use_ai ? reportConfig.value.ai_provider : null,
        attributes: attributesToInclude
      }

      const result = await generateReportFromProcess(params)

      if (result.success) {
        reportResult.value = {
          success: true,
          message: result.message,
          successCount: 1,
          failedCount: 0,
          generatedFiles: [{
            attrName: '综合报告',
            filename: result.filename,
            url: result.download_url
          }],
          failedList: []
        }
        ElMessage.success('报告生成成功')
        refreshHistory()
      } else {
        reportResult.value = {
          success: false,
          message: result.message,
          successCount: 0,
          failedCount: 1,
          generatedFiles: [],
          failedList: [{ attrName: '综合报告', error: result.message }]
        }
      }
    }
  } catch (error) {
    reportResult.value = {
      success: false,
      message: error.message || '报告生成失败',
      successCount: 0,
      failedCount: 1,
      generatedFiles: [],
      failedList: [{ attrName: '未知', error: error.message }]
    }
    ElMessage.error(error.message || '报告生成失败')
  } finally {
    generatingReport.value = false
    generateProgress.value.currentAttr = '完成'
  }
}

// 下载 Word 报告
const downloadWordReport = () => {
  if (reportResult.value?.download_url) {
    window.open(reportResult.value.download_url, '_blank')
  }
}

// 批量下载所有报告
const downloadAllReports = () => {
  if (!reportResult.value?.generatedFiles?.length) {
    ElMessage.warning('没有可下载的报告')
    return
  }

  // 逐个触发下载
  reportResult.value.generatedFiles.forEach((file, index) => {
    setTimeout(() => {
      window.open(file.url, '_blank')
    }, index * 500)  // 每500ms下载一个，避免浏览器阻止
  })

  ElMessage.success(`正在下载 ${reportResult.value.generatedFiles.length} 份报告...`)
}

// 刷新历史记录
const refreshHistory = async () => {
  try {
    reportList.value = await getReportList()
  } catch (error) {
    console.error('获取历史记录失败:', error)
  }
}

// 刷新处理记录
const refreshProcessRecords = async () => {
  try {
    processRecords.value = await getProcessRecords()
  } catch (error) {
    console.error('获取处理记录失败:', error)
  }
}

// 选择历史处理记录
const selectProcessRecord = (record) => {
  // 设置处理结果，使其可以生成报告
  processResult.value = {
    success: true,
    process_id: record.process_id,
    preview: record.preview,
    download_url: `/api/report/download/${encodeURIComponent(record.excel_filename)}`,
    message: `已加载历史记录: ${record.created_at}`
  }
  // 展开报告生成表单
  showReportForm.value = true
  // 重置选择
  selectedAttributes.value = []
  selectedSingleAttributes.value = []
  reportResult.value = null
  ElMessage.success('已加载历史处理记录，请配置报告参数')
}

// 报告模式变化时重置单属性选择
const onReportModeChange = () => {
  selectedSingleAttributes.value = []
}

// 地区选择变化
const onRegionChange = (regionId) => {
  const region = regions.value.find(r => r.id === regionId)
  if (region) {
    reportConfig.value.region_name = region.name
  }
}

// 加载地区列表
const loadRegions = async () => {
  try {
    const response = await getRegions()
    regions.value = response.regions || []
  } catch (error) {
    console.error('获取地区列表失败:', error)
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
  loadRegions()
  refreshHistory()
  refreshProcessRecords()
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

.error-message {
  padding: 20px 0;
}

.action-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

/* 数据预览 */
.preview-section {
  margin: 20px 0;
}

.preview-section h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: #303133;
}

.grade-distribution {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.grade-item {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

/* 报告生成区域 */
.report-section {
  margin-top: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f7fa;
  cursor: pointer;
  transition: background 0.3s;
}

.section-header:hover {
  background: #ebeef5;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.report-form {
  padding: 20px;
  background: #fff;
}

.ai-hint {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.report-result {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 属性选择提示 */
.select-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 全选/清空按钮 */
.select-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

/* 进度条区域 */
.progress-section {
  margin: 20px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.progress-count {
  font-size: 14px;
  color: #409eff;
  font-weight: 600;
}

.progress-current {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.progress-current .is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 结果统计 */
.result-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

/* 生成的文件列表 */
.generated-files {
  margin-top: 20px;
  text-align: left;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #303133;
}

.files-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fff;
}

.file-item-download {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid #f0f2f5;
}

.file-item-download:last-child {
  border-bottom: none;
}

.file-item-download .el-icon {
  color: #409eff;
}

.file-item-download .file-name {
  flex: 1;
  font-size: 14px;
  color: #303133;
}

/* 失败列表 */
.failed-list {
  margin-top: 20px;
  text-align: left;
}

.failed-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.failed-item:last-child {
  border-bottom: none;
}

.error-msg {
  flex: 1;
  font-size: 12px;
  color: #f56c6c;
  word-break: break-all;
}

/* 历史记录卡片 */
.history-card {
  margin-bottom: 20px;
}

.history-list {
  max-height: 300px;
  overflow: auto;
}

/* 文件名标签 */
.file-names {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.file-tag {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-tag {
  background: #e6f7ff;
  color: #1890ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 页面操作 */
.page-actions {
  margin-top: 20px;
}

/* 历史文件按钮 */
.history-btn {
  margin-left: auto;
}

/* 历史文件对话框 */
.history-file-content {
  min-height: 200px;
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
