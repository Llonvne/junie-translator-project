<template>
  <div class="home-container">
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="main-title">欢迎使用 SRT 字幕翻译器</h1>
        <p class="subtitle">
          基于AI的智能字幕翻译工具，支持多种语言和翻译风格
        </p>
        
        <div class="feature-cards">
          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon :size="24" color="#409eff">
                  <Document />
                </el-icon>
                <span>文件翻译</span>
              </div>
            </template>
            <p>上传SRT字幕文件，批量翻译所有字幕条目</p>
            <div class="card-actions">
              <el-button type="primary" @click="$router.push('/file-translator')">
                开始翻译文件
              </el-button>
            </div>
          </el-card>

          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon :size="24" color="#67c23a">
                  <EditPen />
                </el-icon>
                <span>文本翻译</span>
              </div>
            </template>
            <p>快速翻译单个文本段落，实时预览翻译效果</p>
            <div class="card-actions">
              <el-button type="success" @click="$router.push('/text-translator')">
                开始翻译文本
              </el-button>
            </div>
          </el-card>

          <el-card class="feature-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon :size="24" color="#e6a23c">
                  <Setting />
                </el-icon>
                <span>系统设置</span>
              </div>
            </template>
            <p>配置翻译参数、AI模型和提示词风格</p>
            <div class="card-actions">
              <el-button type="warning" @click="$router.push('/settings')">
                打开设置
              </el-button>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 系统状态面板 -->
    <div class="status-section">
      <el-card class="status-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20">
              <Monitor />
            </el-icon>
            <span>系统状态</span>
            <el-button 
              size="small" 
              @click="refreshStatus"
              :loading="loading"
              style="margin-left: auto;"
            >
              刷新
            </el-button>
          </div>
        </template>
        
        <div class="status-grid" v-if="config">
          <div class="status-item">
            <span class="status-label">目标语言:</span>
            <el-tag>{{ config.to_language }}</el-tag>
          </div>
          <div class="status-item">
            <span class="status-label">AI模型:</span>
            <el-tag type="success">{{ config.model }}</el-tag>
          </div>
          <div class="status-item">
            <span class="status-label">服务提供商:</span>
            <el-tag type="info">{{ config.provider }}</el-tag>
          </div>
          <div class="status-item">
            <span class="status-label">提示词风格:</span>
            <el-tag type="warning">{{ config.prompt_style }}</el-tag>
          </div>
        </div>
        
        <div v-else class="loading-placeholder">
          <el-skeleton :rows="2" animated />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, EditPen, Setting, Monitor } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'

const appStore = useAppStore()
const config = ref(null)
const loading = ref(false)

const refreshStatus = async () => {
  loading.value = true
  try {
    const configData = await appStore.loadConfig()
    config.value = configData
    ElMessage.success('状态已刷新')
  } catch (error) {
    ElMessage.error('获取系统状态失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.home-container {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 60px;
}

.main-title {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 16px;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

.feature-card {
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  font-size: 1.1rem;
}

.card-actions {
  margin-top: 20px;
}

.status-section {
  margin-top: 40px;
}

.status-card {
  max-width: 800px;
  margin: 0 auto;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
}

.status-label {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.loading-placeholder {
  padding: 20px;
}

@media (max-width: 768px) {
  .home-container {
    padding: 20px;
  }
  
  .main-title {
    font-size: 2rem;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>