<template>
  <div class="text-translator">
    <div class="page-header">
      <h1>文本翻译</h1>
      <p>快速翻译单个文本段落，实时预览翻译效果</p>
    </div>

    <div class="translator-content">
      <el-row :gutter="30">
        <!-- 输入区域 -->
        <el-col :span="12">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <el-icon :size="20"><EditPen /></el-icon>
                <span>原文输入</span>
                <div class="text-counter">{{ inputText.length }}/5000</div>
              </div>
            </template>

            <el-input
              v-model="inputText"
              type="textarea"
              :rows="15"
              placeholder="请输入要翻译的文本..."
              maxlength="5000"
              show-word-limit
              resize="none"
              class="input-textarea"
            />

            <div class="input-actions">
              <el-button @click="clearInput" :disabled="!inputText">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
              <el-button @click="pasteFromClipboard">
                <el-icon><DocumentCopy /></el-icon>
                粘贴
              </el-button>
              <el-button 
                type="primary" 
                @click="translateText"
                :loading="translating"
                :disabled="!inputText.trim()"
              >
                <el-icon><Right /></el-icon>
                翻译
              </el-button>
            </div>
          </el-card>
        </el-col>

        <!-- 输出区域 -->
        <el-col :span="12">
          <el-card class="output-card">
            <template #header>
              <div class="card-header">
                <el-icon :size="20"><Document /></el-icon>
                <span>翻译结果</span>
                <div class="output-actions" v-if="outputText">
                  <el-button 
                    size="small" 
                    @click="copyToClipboard"
                    :icon="DocumentCopy"
                  >
                    复制
                  </el-button>
                </div>
              </div>
            </template>

            <div class="output-content">
              <div v-if="translating" class="translating-placeholder">
                <el-skeleton :rows="8" animated />
                <div class="translating-text">
                  <el-icon class="rotating"><Loading /></el-icon>
                  正在翻译中...
                </div>
              </div>

              <div v-else-if="outputText" class="output-text">
                <div class="translation-result">{{ outputText }}</div>
              </div>

              <div v-else class="empty-output">
                <el-empty 
                  description="翻译结果将在这里显示"
                  :image-size="120"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 翻译历史 -->
      <el-card class="history-card" v-if="translationHistory.length > 0">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><Clock /></el-icon>
            <span>翻译历史</span>
            <el-button 
              size="small" 
              @click="clearHistory"
              style="margin-left: auto;"
            >
              清空历史
            </el-button>
          </div>
        </template>

        <div class="history-list">
          <div 
            v-for="(item, index) in translationHistory" 
            :key="index"
            class="history-item"
            @click="useHistoryItem(item)"
          >
            <div class="history-original">
              <strong>原文：</strong>{{ truncateText(item.original, 100) }}
            </div>
            <div class="history-translation">
              <strong>译文：</strong>{{ truncateText(item.translation, 100) }}
            </div>
            <div class="history-time">{{ formatTime(item.timestamp) }}</div>
          </div>
        </div>
      </el-card>

      <!-- 快捷示例 -->
      <el-card class="examples-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><Star /></el-icon>
            <span>快捷示例</span>
          </div>
        </template>

        <div class="examples-grid">
          <div 
            v-for="example in examples" 
            :key="example.id"
            class="example-item"
            @click="useExample(example)"
          >
            <div class="example-title">{{ example.title }}</div>
            <div class="example-text">{{ example.text }}</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { 
  EditPen, Document, Delete, DocumentCopy, Right, 
  Loading, Clock, Star 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 响应式数据
const inputText = ref('')
const outputText = ref('')
const translating = ref(false)
const translationHistory = ref([])

// 示例文本
const examples = [
  {
    id: 1,
    title: '电影对话',
    text: 'Hello, how are you doing today?\nI\'m fine, thank you for asking.'
  },
  {
    id: 2,
    title: '新闻标题',
    text: 'Breaking News: Scientists discover new planet in distant galaxy'
  },
  {
    id: 3,
    title: '日常对话',
    text: 'What time is the meeting?\nThe meeting is scheduled for 3 PM.'
  },
  {
    id: 4,
    title: '技术文档',
    text: 'This function returns the current timestamp in milliseconds since epoch.'
  }
]

// 翻译文本
const translateText = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning('请输入要翻译的文本')
    return
  }

  translating.value = true
  outputText.value = ''

  try {
    const response = await appStore.translateText(inputText.value.trim())
    outputText.value = response.translated_text
    
    // 添加到历史记录
    translationHistory.value.unshift({
      original: inputText.value.trim(),
      translation: response.translated_text,
      timestamp: new Date()
    })
    
    // 限制历史记录数量
    if (translationHistory.value.length > 20) {
      translationHistory.value = translationHistory.value.slice(0, 20)
    }
    
    ElMessage.success('翻译完成')
  } catch (error) {
    ElMessage.error('翻译失败: ' + error.message)
  } finally {
    translating.value = false
  }
}

// 清空输入
const clearInput = () => {
  inputText.value = ''
  outputText.value = ''
}

// 从剪贴板粘贴
const pasteFromClipboard = async () => {
  try {
    const text = await navigator.clipboard.readText()
    inputText.value = text
    ElMessage.success('已从剪贴板粘贴文本')
  } catch (error) {
    ElMessage.error('无法从剪贴板读取内容')
  }
}

// 复制到剪贴板
const copyToClipboard = async () => {
  if (!outputText.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }

  try {
    await navigator.clipboard.writeText(outputText.value)
    ElMessage.success('翻译结果已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 使用历史记录项
const useHistoryItem = (item) => {
  inputText.value = item.original
  outputText.value = item.translation
}

// 使用示例
const useExample = (example) => {
  inputText.value = example.text
  outputText.value = ''
}

// 清空历史
const clearHistory = () => {
  translationHistory.value = []
  ElMessage.success('历史记录已清空')
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 格式化时间
const formatTime = (timestamp) => {
  return timestamp.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.text-translator {
  padding: 20px;
  max-width: 1400px;
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

.translator-content {
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

.text-counter {
  margin-left: auto;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.output-actions {
  margin-left: auto;
}

.input-textarea {
  font-size: 14px;
  line-height: 1.6;
}

.input-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 16px;
}

.output-content {
  min-height: 400px;
  display: flex;
  flex-direction: column;
}

.translating-placeholder {
  flex: 1;
}

.translating-text {
  text-align: center;
  margin-top: 20px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.output-text {
  flex: 1;
}

.translation-result {
  padding: 20px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
}

.empty-output {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-fill-color-lighter);
}

.history-original,
.history-translation {
  margin-bottom: 8px;
  line-height: 1.5;
}

.history-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: right;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.example-item {
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.example-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-fill-color-lighter);
}

.example-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.example-text {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .text-translator {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .input-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .examples-grid {
    grid-template-columns: 1fr;
  }
}
</style>