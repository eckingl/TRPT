<template>
  <el-dialog
    v-model="visible"
    title="AI 配置管理"
    width="700px"
    :close-on-click-modal="false"
  >
    <div class="ai-settings">
      <!-- 配置列表 -->
      <div class="config-list">
        <div class="list-header">
          <span>已保存的配置</span>
          <el-button type="primary" size="small" @click="showAddForm">
            <el-icon><Plus /></el-icon>
            新增配置
          </el-button>
        </div>

        <el-table :data="configs" v-loading="loading" empty-text="暂无配置">
          <el-table-column prop="name" label="名称" width="120" />
          <el-table-column prop="provider" label="提供商" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="getProviderTagType(row.provider)">
                {{ getProviderLabel(row.provider) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="model" label="模型" width="140" />
          <el-table-column prop="api_key_masked" label="API Key" min-width="120">
            <template #default="{ row }">
              <code class="api-key">{{ row.api_key_masked }}</code>
            </template>
          </el-table-column>
          <el-table-column label="默认" width="70" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="testConfig(row)">
                测试
              </el-button>
              <el-button size="small" link type="primary" @click="editConfig(row)">
                编辑
              </el-button>
              <el-button
                size="small"
                link
                type="primary"
                @click="setDefault(row)"
                :disabled="row.is_default"
              >
                设为默认
              </el-button>
              <el-button size="small" link type="danger" @click="deleteConfig(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 新增/编辑表单 -->
      <el-dialog
        v-model="formVisible"
        :title="isEdit ? '编辑配置' : '新增配置'"
        width="500px"
        append-to-body
      >
        <el-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          label-width="100px"
        >
          <el-form-item label="配置名称" prop="name">
            <el-input v-model="formData.name" placeholder="例如：DeepSeek 生产环境" />
          </el-form-item>

          <el-form-item label="提供商" prop="provider">
            <el-select v-model="formData.provider" placeholder="选择 AI 提供商" style="width: 100%">
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="通义千问" value="qwen" />
              <el-option label="OpenAI" value="openai" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </el-form-item>

          <el-form-item label="API Key" prop="api_key">
            <el-input
              v-model="formData.api_key"
              :placeholder="isEdit ? '留空则不修改' : '请输入 API Key'"
              show-password
            />
          </el-form-item>

          <el-form-item
            label="API 地址"
            prop="base_url"
            v-if="formData.provider === 'custom' || formData.provider === 'openai'"
          >
            <el-input
              v-model="formData.base_url"
              placeholder="例如：https://api.openai.com/v1"
            />
          </el-form-item>

          <el-form-item label="模型名称" prop="model">
            <el-input v-model="formData.model" :placeholder="getModelPlaceholder()" />
            <div class="form-tip">
              {{ getModelTip() }}
            </div>
          </el-form-item>

          <el-form-item label="设为默认">
            <el-switch v-model="formData.is_default" />
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            {{ isEdit ? '保存' : '添加' }}
          </el-button>
        </template>
      </el-dialog>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getAIConfigs,
  createAIConfig,
  updateAIConfig,
  deleteAIConfig as deleteAIConfigApi,
  setDefaultAIConfig,
  testAIConfig
} from '@/api/index.js'

const visible = defineModel({ type: Boolean, default: false })

const loading = ref(false)
const configs = ref([])
const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)

const formData = reactive({
  name: '',
  provider: 'deepseek',
  api_key: '',
  base_url: '',
  model: '',
  is_default: false
})

const formRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  api_key: [
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && !value) {
          callback(new Error('请输入 API Key'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  model: [{ required: true, message: '请输入模型名称', trigger: 'blur' }]
}

// 加载配置列表
const loadConfigs = async () => {
  loading.value = true
  try {
    const res = await getAIConfigs()
    configs.value = res.configs || []
  } catch (err) {
    ElMessage.error('加载配置失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

// 监听弹窗打开
watch(visible, (val) => {
  if (val) {
    loadConfigs()
  }
})

// 显示新增表单
const showAddForm = () => {
  isEdit.value = false
  editingId.value = null
  Object.assign(formData, {
    name: '',
    provider: 'deepseek',
    api_key: '',
    base_url: '',
    model: 'deepseek-chat',
    is_default: configs.value.length === 0
  })
  formVisible.value = true
}

// 编辑配置
const editConfig = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(formData, {
    name: row.name,
    provider: row.provider,
    api_key: '',
    base_url: row.base_url || '',
    model: row.model,
    is_default: row.is_default
  })
  formVisible.value = true
}

// 提交表单
const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = { ...formData }
    if (isEdit.value && !data.api_key) {
      delete data.api_key
    }

    if (isEdit.value) {
      await updateAIConfig(editingId.value, data)
      ElMessage.success('配置已更新')
    } else {
      await createAIConfig(data)
      ElMessage.success('配置已添加')
    }
    formVisible.value = false
    loadConfigs()
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    submitting.value = false
  }
}

// 删除配置
const deleteConfig = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除配置 "${row.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await deleteAIConfigApi(row.id)
    ElMessage.success('已删除')
    loadConfigs()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message)
    }
  }
}

// 设为默认
const setDefault = async (row) => {
  try {
    await setDefaultAIConfig(row.id)
    ElMessage.success('已设为默认配置')
    loadConfigs()
  } catch (err) {
    ElMessage.error(err.message)
  }
}

// 测试配置
const testConfig = async (row) => {
  try {
    ElMessage.info('正在测试连接...')
    const res = await testAIConfig(row.id)
    if (res.success) {
      ElMessage.success(res.message)
    } else {
      ElMessage.error(res.message)
    }
  } catch (err) {
    ElMessage.error('测试失败: ' + err.message)
  }
}

// 工具函数
const getProviderLabel = (provider) => {
  const map = {
    deepseek: 'DeepSeek',
    qwen: '通义千问',
    openai: 'OpenAI',
    custom: '自定义'
  }
  return map[provider] || provider
}

const getProviderTagType = (provider) => {
  const map = {
    deepseek: 'primary',
    qwen: 'success',
    openai: 'warning',
    custom: 'info'
  }
  return map[provider] || ''
}

const getModelPlaceholder = () => {
  const map = {
    deepseek: 'deepseek-chat',
    qwen: 'qwen-plus',
    openai: 'gpt-4o-mini',
    custom: '输入模型名称'
  }
  return map[formData.provider] || '输入模型名称'
}

const getModelTip = () => {
  const map = {
    deepseek: '推荐：deepseek-chat、deepseek-reasoner',
    qwen: '推荐：qwen-plus、qwen-turbo',
    openai: '推荐：gpt-4o-mini、gpt-4o',
    custom: '请参考服务商文档'
  }
  return map[formData.provider] || ''
}

// 监听 provider 变化，自动填充模型
watch(() => formData.provider, (val) => {
  if (!isEdit.value) {
    const defaultModels = {
      deepseek: 'deepseek-chat',
      qwen: 'qwen-plus',
      openai: 'gpt-4o-mini',
      custom: ''
    }
    formData.model = defaultModels[val] || ''
  }
})
</script>

<style scoped>
.ai-settings {
  min-height: 300px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
}

.api-key {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
