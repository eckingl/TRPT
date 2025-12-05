<template>
  <div class="upload-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据上传</span>
        </div>
      </template>

      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :show-file-list="false"
        accept=".csv,.xlsx,.xls"
        @change="handleFileChange"
      >
        <el-icon class="el-icon--upload" :size="60"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 CSV、Excel (.xlsx/.xls) 文件，文件大小不超过 50MB
          </div>
        </template>
      </el-upload>

      <div v-if="store.uploadedFile" class="file-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">
            {{ store.uploadedFile.filename }}
          </el-descriptions-item>
          <el-descriptions-item label="数据行数">
            {{ store.uploadedFile.rows }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div v-if="store.dataPreview.length > 0" class="data-preview">
        <h4>数据预览</h4>
        <el-table :data="store.dataPreview" border max-height="300">
          <el-table-column
            v-for="col in store.columns"
            :key="col"
            :prop="col"
            :label="col"
            min-width="120"
          />
        </el-table>
      </div>
    </el-card>

    <div class="page-actions">
      <el-button @click="$router.push('/')">返回首页</el-button>
      <el-button
        type="primary"
        :disabled="!store.hasData"
        @click="$router.push('/config')"
      >
        下一步：配置项目
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadFile } from '@/api'
import { useProjectStore } from '@/stores/project'

const store = useProjectStore()

const handleFileChange = async (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return

  try {
    const result = await uploadFile(file)
    store.setUploadedFile(result, result.preview, result.columns)
    ElMessage.success('文件上传成功')
  } catch (error) {
    ElMessage.error(error.message || '文件上传失败')
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  font-size: 18px;
  font-weight: bold;
}

.upload-area {
  margin-bottom: 20px;
}

.file-info {
  margin: 20px 0;
}

.data-preview {
  margin-top: 20px;
}

.data-preview h4 {
  margin-bottom: 10px;
  color: #303133;
}

.page-actions {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
}
</style>
