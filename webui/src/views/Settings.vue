<template>
  <div class="settings">
    <div class="page-header">
      <h1>系统设置</h1>
      <p>配置翻译参数、AI模型和提示词风格</p>
    </div>

    <div class="settings-content">
      <el-row :gutter="30">
        <!-- 当前配置 -->
        <el-col :span="12">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <el-icon :size="20"><Setting /></el-icon>
                <span>当前配置</span>
                <el-button 
                  size="small" 
                  @click="refreshConfig"
                  :loading="loading"
                  style="margin-left: auto;"
                >
                  刷新
                </el-button>
              </div>
            </template>

            <div v-if="config" class="config-display">
              <div class="config-section">
                <h3>语言设置</h3>
                <div class="config-grid">
                  <div class="config-item">
                    <span class="config-label">源语言:</span>
                    <el-tag>{{ config.from_language }}</el-tag>
                  </div>
                  <div class="config-item">
                    <span class="config-label">目标语言:</span>
                    <el-tag type="success">{{ config.to_language }}</el-tag>
                  </div>
                </div>
              </div>

              <div class="config-section">
                <h3>AI服务设置</h3>
                <div class="config-grid">
                  <div class="config-item">
                    <span class="config-label">服务提供商:</span>
                    <el-tag type="info">{{ config.provider }}</el-tag>
                  </div>
                  <div class="config-item">
                    <span class="config-label">AI模型:</span>
                    <el-tag type="warning">{{ config.model }}</el-tag>
                  </div>
                </div>
              </div>

              <div class="config-section">
                <h3>翻译设置</h3>
                <div class="config-grid">
                  <div class="config-item">
                    <span class="config-label">提示词风格:</span>
                    <el-tag type="danger">{{ config.prompt_style }}</el-tag>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="loading-placeholder">
              <el-skeleton :rows="6" animated />
            </div>
          </el-card>
        </el-col>

        <!-- 系统信息 -->
        <el-col :span="12">
          <el-card class="system-info-card">
            <template #header>
              <div class="card-header">
                <el-icon :size="20"><Monitor /></el-icon>
                <span>系统信息</span>
                <el-button 
                  size="small" 
                  @click="checkSystemHealth"
                  :loading="healthChecking"
                  style="margin-left: auto;"
                >
                  健康检查
                </el-button>
              </div>
            </template>

            <div class="system-info">
              <div class="info-section">
                <h3>服务状态</h3>
                <div class="status-indicator">
                  <el-icon 
                    :size="20" 
                    :color="healthStatus === 'healthy' ? '#67c23a' : '#f56c6c'"
                  >
                    <component :is="healthStatus === 'healthy' ? 'SuccessFilled' : 'CircleCloseFilled'" />
                  </el-icon>
                  <span :class="['status-text', healthStatus]">
                    {{ healthStatus === 'healthy' ? '运行正常' : '服务异常' }}
                  </span>
                </div>
              </div>

              <div class="info-section">
                <h3>API连接</h3>
                <div class="connection-test">
                  <el-button 
                    @click="testConnection" 
                    :loading="testing"
                    size="small"
                    type="primary"
                  >
                    测试连接
                  </el-button>
                  <span v-if="testResult" :class="['test-result', testResult.type]">
                    {{ testResult.message }}
                  </span>
                </div>
              </div>

              <div class="info-section">
                <h3>功能介绍</h3>
                <div class="feature-list">
                  <div class="feature-item">
                    <el-icon color="#409eff"><Document /></el-icon>
                    <span>支持SRT字幕文件批量翻译</span>
                  </div>
                  <div class="feature-item">
                    <el-icon color="#67c23a"><EditPen /></el-icon>
                    <span>实时文本翻译功能</span>
                  </div>
                  <div class="feature-item">
                    <el-icon color="#e6a23c"><Setting /></el-icon>
                    <span>多种提示词风格选择</span>
                  </div>
                  <div class="feature-item">
                    <el-icon color="#f56c6c"><Star /></el-icon>
                    <span>支持多种AI服务提供商</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 使用说明 -->
      <el-card class="help-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><QuestionFilled /></el-icon>
            <span>使用说明</span>
          </div>
        </template>

        <el-collapse>
          <el-collapse-item title="如何配置AI服务?" name="1">
            <div class="help-content">
              <p>1. 修改项目根目录下的 <code>config.json</code> 文件</p>
              <p>2. 设置正确的AI服务提供商和API密钥</p>
              <p>3. 选择合适的模型和提示词风格</p>
              <p>4. 重启服务以使配置生效</p>
            </div>
          </el-collapse-item>

          <el-collapse-item title="支持哪些AI服务提供商?" name="2">
            <div class="help-content">
              <p>目前支持以下AI服务提供商：</p>
              <ul>
                <li><strong>OpenAI:</strong> GPT-3.5-turbo, GPT-4</li>
                <li><strong>DeepSeek:</strong> deepseek-chat, deepseek-reasoner</li>
                <li><strong>Mock:</strong> 测试用模拟服务</li>
              </ul>
            </div>
          </el-collapse-item>

          <el-collapse-item title="如何选择提示词风格?" name="3">
            <div class="help-content">
              <p>不同的提示词风格适用于不同的翻译场景：</p>
              <ul>
                <li><strong>default:</strong> 通用翻译风格</li>
                <li><strong>formal:</strong> 正式文档翻译</li>
                <li><strong>casual:</strong> 日常对话翻译</li>
                <li><strong>technical:</strong> 技术文档翻译</li>
                <li><strong>subtitle:</strong> 字幕翻译专用</li>
              </ul>
            </div>
          </el-collapse-item>

          <el-collapse-item title="翻译质量如何优化?" name="4">
            <div class="help-content">
              <p>提高翻译质量的建议：</p>
              <ul>
                <li>选择合适的提示词风格</li>
                <li>使用更高级的AI模型</li>
                <li>调整并发数量以平衡速度和质量</li>
                <li>对于重要内容建议人工校对</li>
              </ul>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Setting, Monitor, Document, EditPen, Star,
  QuestionFilled, SuccessFilled, CircleCloseFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 响应式数据
const config = ref(null)
const loading = ref(false)
const healthStatus = ref('unknown')
const healthChecking = ref(false)
const testing = ref(false)
const testResult = ref(null)

// 刷新配置
const refreshConfig = async () => {
  loading.value = true
  try {
    const configData = await appStore.loadConfig()
    config.value = configData
    ElMessage.success('配置已刷新')
  } catch (error) {
    ElMessage.error('获取配置失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 检查系统健康状态
const checkSystemHealth = async () => {
  healthChecking.value = true
  try {
    const status = await appStore.checkHealth()
    healthStatus.value = status
    ElMessage.success(status === 'healthy' ? '系统运行正常' : '系统存在问题')
  } catch (error) {
    healthStatus.value = 'unhealthy'
    ElMessage.error('健康检查失败: ' + error.message)
  } finally {
    healthChecking.value = false
  }
}

// 测试API连接
const testConnection = async () => {
  testing.value = true
  testResult.value = null
  
  try {
    const response = await appStore.translateText('Hello, world!')
    testResult.value = {
      type: 'success',
      message: '✅ API连接正常'
    }
    ElMessage.success('API连接测试成功')
  } catch (error) {
    testResult.value = {
      type: 'error',
      message: '❌ API连接失败: ' + error.message
    }
    ElMessage.error('API连接测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  refreshConfig()
  checkSystemHealth()
})
</script>

<style scoped>
.settings {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.page-header p {
  font-size: 1.1rem;
  color: var(--el-text-color-secondary);
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.config-display {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section h3 {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 8px;
}

.config-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.config-label {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.loading-placeholder {
  padding: 20px 0;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-section h3 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-text.healthy {
  color: #67c23a;
  font-weight: 600;
}

.status-text.unhealthy {
  color: #f56c6c;
  font-weight: 600;
}

.connection-test {
  display: flex;
  align-items: center;
  gap: 16px;
}

.test-result.success {
  color: #67c23a;
  font-weight: 500;
}

.test-result.error {
  color: #f56c6c;
  font-weight: 500;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.help-content {
  padding: 16px 0;
  line-height: 1.6;
}

.help-content p {
  margin: 8px 0;
}

.help-content ul {
  margin: 12px 0;
  padding-left: 20px;
}

.help-content li {
  margin: 6px 0;
}

.help-content code {
  background: var(--el-fill-color-lighter);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

@media (max-width: 768px) {
  .settings {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .config-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .connection-test {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>