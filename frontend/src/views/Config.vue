<template>
  <div class="config-page">
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
      <el-button @click="$router.push('/upload')">上一步</el-button>
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
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores/project'

const store = useProjectStore()
const formRef = ref()

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
