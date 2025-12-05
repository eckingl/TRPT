<template>
  <div class="report-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报告生成</span>
        </div>
      </template>

      <div v-if="topics.length === 0" class="empty-state">
        <el-empty description="暂无可用专题">
          <el-alert
            title="专题将在后续阶段添加"
            type="info"
            show-icon
            :closable="false"
          />
        </el-empty>
      </div>

      <div v-else class="topic-list">
        <el-radio-group v-model="selectedTopic">
          <el-radio
            v-for="topic in topics"
            :key="topic.id"
            :label="topic.id"
            border
          >
            {{ topic.name }}
          </el-radio>
        </el-radio-group>
      </div>

      <el-divider />

      <div class="generate-section">
        <el-button
          type="primary"
          size="large"
          :disabled="!selectedTopic"
          :loading="isGenerating"
          @click="handleGenerate"
        >
          <el-icon><Document /></el-icon>
          生成报告
        </el-button>
      </div>

      <div v-if="reportPath" class="result-section">
        <el-result
          icon="success"
          title="报告生成成功"
          :sub-title="reportPath"
        >
          <template #extra>
            <el-button type="primary" @click="handleDownload">
              下载报告
            </el-button>
          </template>
        </el-result>
      </div>
    </el-card>

    <div class="page-actions">
      <el-button @click="$router.push('/config')">上一步</el-button>
      <el-button @click="$router.push('/')">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getTopics, generateReport } from '@/api'
import { useProjectStore } from '@/stores/project'

const store = useProjectStore()
const topics = ref([])
const selectedTopic = ref('')
const isGenerating = ref(false)
const reportPath = ref('')

onMounted(async () => {
  try {
    topics.value = await getTopics()
  } catch (error) {
    console.error('获取专题列表失败:', error)
  }
})

const handleGenerate = async () => {
  if (!selectedTopic.value) {
    ElMessage.warning('请选择专题')
    return
  }

  isGenerating.value = true
  reportPath.value = ''

  try {
    const result = await generateReport(selectedTopic.value, store.config)
    reportPath.value = result.report_path
    ElMessage.success('报告生成成功')
  } catch (error) {
    ElMessage.error(error.message || '报告生成失败')
  } finally {
    isGenerating.value = false
  }
}

const handleDownload = () => {
  ElMessage.info('下载功能将在 P4 阶段实现')
}
</script>

<style scoped>
.report-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.empty-state {
  padding: 40px 0;
}

.topic-list {
  padding: 20px 0;
}

.topic-list .el-radio {
  margin: 10px;
}

.generate-section {
  text-align: center;
  padding: 20px 0;
}

.result-section {
  margin-top: 20px;
}

.page-actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
}
</style>
