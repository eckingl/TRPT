<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-header class="app-header">
        <div class="header-left">
          <el-icon :size="24"><Document /></el-icon>
          <span class="app-title">土壤普查报告系统</span>
        </div>
        <el-menu
          :default-active="currentRoute"
          mode="horizontal"
          :ellipsis="false"
          router
          class="header-menu"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/attribute-process">属性图处理</el-menu-item>
          <el-menu-item index="/upload">数据上传</el-menu-item>
          <el-menu-item index="/config">项目配置</el-menu-item>
          <el-menu-item index="/report">报告生成</el-menu-item>
          <el-menu-item index="/data-manage">数据管理</el-menu-item>
        </el-menu>
        <div class="header-right">
          <el-tooltip content="AI 配置" placement="bottom">
            <el-button
              circle
              @click="showAISettings = true"
            >
              <el-icon><Setting /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- AI 配置弹窗 -->
      <AISettingsDialog v-model="showAISettings" />
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Setting } from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import AISettingsDialog from '@/components/AISettingsDialog.vue'

const route = useRoute()
const currentRoute = computed(() => route.path)
const showAISettings = ref(false)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue',
    Arial, 'Noto Sans', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 40px;
}

.header-left .el-icon {
  color: var(--el-color-primary);
}

.app-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  white-space: nowrap;
}

.app-header .el-menu {
  border-bottom: none;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  margin-left: 20px;
}

.app-main {
  flex: 1;
  padding: 20px;
}
</style>
