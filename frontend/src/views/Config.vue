<template>
  <div class="config-page">
    <!-- 当前选择信息 -->
    <div v-if="store.hasSelection" class="current-selection">
      <el-tag>{{ store.selectedCategory === 'soil_survey' ? '土壤普查' : '耕地质量' }}</el-tag>
      <el-icon><ArrowRight /></el-icon>
      <el-tag type="success">{{ getTopicName() }}</el-tag>
      <el-icon><ArrowRight /></el-icon>
      <el-tag type="warning">{{ store.selectedRegion?.name }}</el-tag>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目配置</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="store.config"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="区域名称" prop="region_name">
          <el-input
            v-model="store.config.region_name"
            placeholder="例如：XX县"
          />
        </el-form-item>

        <el-form-item label="普查年份" prop="survey_year">
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

      <el-divider>分级标准配置</el-divider>

      <el-alert
        title="分级标准配置将在 P2 阶段实现"
        type="info"
        show-icon
        :closable="false"
      />
    </el-card>

    <div class="page-actions">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <el-button type="primary" @click="handleSave">保存配置</el-button>
      <el-button
        type="success"
        :disabled="!store.isConfigured"
        @click="$router.push('/report')"
      >
        下一步：生成报告
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'

const router = useRouter()
const store = useProjectStore()
const formRef = ref()

// 专题名称映射
const topicNames = {
  attribute_map: '属性图',
  type_map: '类型图',
  suitability: '适宜性评价',
  grade_eval: '等级评价'
}

const getTopicName = () => {
  return topicNames[store.selectedTopic] || store.selectedTopic
}

const surveyYear = computed({
  get: () => store.config.survey_year?.toString() || '',
  set: (val) => {
    store.config.survey_year = val ? parseInt(val, 10) : new Date().getFullYear()
  }
})

const historicalYear = computed({
  get: () => store.config.historical_year?.toString() || '',
  set: (val) => {
    store.config.historical_year = val ? parseInt(val, 10) : null
  }
})

const rules = {
  region_name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
  survey_year: [{ required: true, message: '请选择普查年份', trigger: 'change' }]
}

const goBack = () => {
  router.push('/')
}

const handleSave = async () => {
  try {
    await formRef.value?.validate()
    await store.saveConfig()
    ElMessage.success('配置保存成功')
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.message || '保存失败')
    }
  }
}
</script>

<style scoped>
.config-page {
  max-width: 700px;
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

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.page-actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
}
</style>
