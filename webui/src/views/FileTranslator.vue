<template>
  <div class="file-translator">
    <div class="page-header">
      <h1>SRT文件翻译</h1>
      <p>上传SRT字幕文件进行批量翻译</p>
    </div>

    <div class="translator-content">
      <!-- 上传区域 -->
      <el-card class="upload-card" v-if="!translating && !result">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><Upload /></el-icon>
            <span>上传SRT文件</span>
          </div>
        </template>

        <el-upload
          class="upload-dragger"
          drag
          :show-file-list="false"
          :before-upload="handleFileSelect"
          accept=".srt"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将SRT文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传.srt格式的字幕文件，且不超过10MB
            </div>
          </template>
        </el-upload>

        <div class="upload-options" v-if="selectedFile">
          <h3>文件信息</h3>
          <div class="file-info">
            <p><strong>文件名:</strong> {{ selectedFile.name }}</p>
            <p><strong>文件大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
          </div>

          <div class="translation-settings">
            <h3>翻译设置</h3>
            <el-form :model="settings" label-width="120px">
              <el-form-item label="并发数量:">
                <el-slider
                  v-model="settings.maxConcurrent"
                  :min="1"
                  :max="20"
                  :step="1"
                  show-stops
                  show-input
                  :show-input-controls="false"
                />
                <div class="setting-tip">
                  并发数量越高翻译越快，但可能会增加API调用成本
                </div>
              </el-form-item>
            </el-form>
          </div>

          <div class="upload-actions">
            <el-button @click="clearFile" size="large">
              <el-icon><Delete /></el-icon>
              清除文件
            </el-button>
            <el-button type="primary" @click="startTranslation" size="large">
              <el-icon><Right /></el-icon>
              开始翻译
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 翻译进度 -->
      <el-card v-if="translating" class="progress-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><Loading /></el-icon>
            <span>正在翻译中...</span>
          </div>
        </template>

        <div class="progress-content">
          <div class="progress-info">
            <h3>{{ selectedFile?.name }}</h3>
            <p>请耐心等待翻译完成，这可能需要几分钟时间</p>
          </div>

          <div class="progress-animation">
            <el-progress
              type="circle"
              :percentage="100"
              :indeterminate="true"
              :width="120"
            />
          </div>

          <div class="progress-tips">
            <p>💡 翻译时间取决于文件大小和并发设置</p>
            <p>💡 请保持页面开启直到翻译完成</p>
          </div>
        </div>
      </el-card>

      <!-- 翻译结果 -->
      <el-card v-if="result && !translating" class="result-card">
        <template #header>
          <div class="card-header">
            <el-icon :size="20" color="#67c23a"><SuccessFilled /></el-icon>
            <span>翻译完成</span>
          </div>
        </template>

        <div class="result-content">
          <el-result
            icon="success"
            :title="result.message"
            :sub-title="`输出文件: ${result.output_filename}`"
          >
            <template #extra>
              <div class="result-actions">
                <el-button 
                  type="primary" 
                  size="large"
                  @click="downloadResult"
                >
                  <el-icon><Download /></el-icon>
                  下载翻译文件
                </el-button>
                <el-button 
                  size="large"
                  @click="resetTranslator"
                >
                  <el-icon><RefreshLeft /></el-icon>
                  翻译新文件
                </el-button>
              </div>
            </template>
          </el-result>
        </div>
      </el-card>

      <!-- 历史文件 -->
      <el-card class="history-card" v-if="!translating">
        <template #header>
          <div class="card-header">
            <el-icon :size="20"><FolderOpened /></el-icon>
            <span>历史翻译文件</span>
            <el-button 
              size="small" 
              @click="refreshHistory"
              :loading="historyLoading"
              style="margin-left: auto;"
            >
              刷新
            </el-button>
          </div>
        </template>

        <div v-if="historyFiles.length > 0">
          <el-table :data="historyFiles" style="width: 100%">
            <el-table-column prop="name" label="文件名" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="downloadFile(scope.row)"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="empty-history">
          <el-empty description="暂无历史翻译文件" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Upload, UploadFilled, Delete, Right, Loading, 
  SuccessFilled, Download, RefreshLeft, FolderOpened 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// 响应式数据
const selectedFile = ref(null)
const translating = ref(false)
const result = ref(null)
const historyFiles = ref([])
const historyLoading = ref(false)

const settings = ref({
  maxConcurrent: 5
})

// 文件选择处理
const handleFileSelect = (file) => {
  if (!file.name.endsWith('.srt')) {
    ElMessage.error('请选择SRT格式的字幕文件')
    return false
  }
  
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  selectedFile.value = file
  return false // 阻止自动上传
}

// 清除文件
const clearFile = () => {
  selectedFile.value = null
}

// 开始翻译
const startTranslation = async () => {
  if (!selectedFile.value) {
    ElMessage.error('请先选择文件')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要开始翻译这个文件吗？翻译过程可能需要几分钟时间。',
      '确认翻译',
      {
        confirmButtonText: '开始翻译',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    translating.value = true
    result.value = null

    const response = await appStore.translateFile(
      selectedFile.value, 
      settings.value.maxConcurrent
    )

    result.value = response
    ElMessage.success('文件翻译完成！')
    refreshHistory()

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('翻译失败: ' + error.message)
    }
  } finally {
    translating.value = false
  }
}

// 下载翻译结果
const downloadResult = () => {
  if (result.value?.output_filename) {
    downloadFile({ name: result.value.output_filename })
  }
}

// 下载文件
const downloadFile = (file) => {
  const url = appStore.downloadFile(file.name)
  const link = document.createElement('a')
  link.href = url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 重置翻译器
const resetTranslator = () => {
  selectedFile.value = null
  result.value = null
  translating.value = false
}

// 刷新历史文件
const refreshHistory = async () => {
  historyLoading.value = true
  try {
    const files = await appStore.listFiles()
    historyFiles.value = files.map(name => ({ name }))
  } catch (error) {
    ElMessage.error('获取历史文件失败: ' + error.message)
  } finally {
    historyLoading.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  refreshHistory()
})
</script>

<style scoped>
.file-translator {
  padding: 20px;
  max-width: 1000px;
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

.upload-card {
  min-height: 400px;
}

.upload-dragger {
  width: 100%;
}

.upload-options {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.upload-options h3 {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
}

.file-info {
  background: var(--el-fill-color-lighter);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.file-info p {
  margin: 4px 0;
}

.setting-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
}

.upload-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 24px;
}

.progress-card {
  text-align: center;
}

.progress-content {
  padding: 40px 20px;
}

.progress-info h3 {
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.progress-animation {
  margin: 40px 0;
}

.progress-tips {
  margin-top: 30px;
}

.progress-tips p {
  margin: 8px 0;
  color: var(--el-text-color-secondary);
}

.result-card {
  text-align: center;
}

.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.empty-history {
  padding: 40px 20px;
}

@media (max-width: 768px) {
  .file-translator {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .upload-actions,
  .result-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>