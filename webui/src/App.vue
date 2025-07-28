<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 头部导航 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <el-icon :size="28" color="#409eff">
              <Document />
            </el-icon>
            <h1>SRT字幕翻译器</h1>
          </div>
          
          <div class="header-actions">
            <el-button 
              @click="toggleTheme" 
              :icon="isDark ? Sunny : Moon" 
              circle
              size="large"
            />
            <el-button 
              @click="checkHealth" 
              :loading="healthChecking"
              :type="serverStatus === 'healthy' ? 'success' : 'danger'"
              :icon="serverStatus === 'healthy' ? Check : Close"
              circle
              size="large"
            />
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, Sunny, Moon, Check, Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const isDark = ref(false)
const healthChecking = ref(false)
const serverStatus = ref('unknown')

// 切换主题
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

// 检查服务器健康状态
const checkHealth = async () => {
  healthChecking.value = true
  try {
    const status = await appStore.checkHealth()
    serverStatus.value = status
    ElMessage.success(status === 'healthy' ? '服务器运行正常' : '服务器异常')
  } catch (error) {
    serverStatus.value = 'unhealthy'
    ElMessage.error('无法连接到服务器')
  } finally {
    healthChecking.value = false
  }
}

onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  background: var(--el-bg-color-page);
  min-height: calc(100vh - 60px);
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style>