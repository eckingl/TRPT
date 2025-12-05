/**
 * Vue Router 配置
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('@/views/Upload.vue'),
    meta: { title: '数据上传' }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/Config.vue'),
    meta: { title: '项目配置' }
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    meta: { title: '报告生成' }
  },
  {
    path: '/attribute-process',
    name: 'AttributeProcess',
    component: () => import('@/views/AttributeProcess.vue'),
    meta: { title: '属性图处理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由标题
router.beforeEach((to) => {
  document.title = `${to.meta.title || '首页'} - 土壤普查报告系统`
})

export default router
