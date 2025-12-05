<template>
  <div class="home">
    <div class="welcome">
      <el-icon class="welcome-icon" :size="80">
        <Document />
      </el-icon>
      <h1>农业土壤普查报告生成系统</h1>
      <p class="description">快速生成专业的土壤普查分析报告</p>
    </div>

    <div class="steps">
      <el-steps :active="currentStep" align-center>
        <el-step title="上传数据" description="上传 CSV/Excel 数据文件" />
        <el-step title="配置项目" description="设置区域和分级标准" />
        <el-step title="生成报告" description="选择专题并生成报告" />
      </el-steps>
    </div>

    <div class="actions">
      <el-button type="primary" size="large" @click="$router.push('/upload')">
        <el-icon><Upload /></el-icon>
        开始使用
      </el-button>
    </div>

    <div class="status">
      <el-card shadow="hover">
        <template #header>
          <span>系统状态</span>
        </template>
        <div class="status-item">
          <span>后端服务：</span>
          <el-tag :type="healthStatus === 'ok' ? 'success' : 'danger'">
            {{ healthStatus === 'ok' ? '正常' : '异常' }}
          </el-tag>
        </div>
        <div class="status-item">
          <span>版本：</span>
          <span>{{ version }}</span>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Document, Upload } from '@element-plus/icons-vue'
import { checkHealth } from '@/api'
import { useProjectStore } from '@/stores/project'

const store = useProjectStore()
const healthStatus = ref('checking')
const version = ref('-')

const currentStep = computed(() => {
  if (!store.hasData) return 0
  if (!store.isConfigured) return 1
  return 2
})

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
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.welcome {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-icon {
  color: var(--el-color-primary);
  margin-bottom: 20px;
}

.welcome h1 {
  margin: 0 0 10px;
  font-size: 28px;
  color: #303133;
}

.description {
  color: #909399;
  font-size: 16px;
}

.steps {
  margin-bottom: 40px;
}

.actions {
  text-align: center;
  margin-bottom: 40px;
}

.status {
  max-width: 300px;
  margin: 0 auto;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.status-item:not(:last-child) {
  border-bottom: 1px solid #ebeef5;
}
</style>
