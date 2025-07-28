import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    
    if (error.response) {
      // 服务器响应了错误状态码
      const message = error.response.data?.detail || error.response.data?.message || `HTTP ${error.response.status}`
      throw new Error(message)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      throw new Error('无法连接到服务器')
    } else {
      // 其他错误
      throw new Error(error.message || '未知错误')
    }
  }
)

const apiService = {
  // 健康检查
  checkHealth() {
    return api.get('/health')
  },

  // 获取配置
  getConfig() {
    return api.get('/config')
  },

  // 翻译文本
  translateText(data) {
    return api.post('/translate/text', data)
  },

  // 翻译文件
  translateFile(file, maxConcurrent = 5) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('max_concurrent', maxConcurrent)
    
    return api.post('/translate/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5分钟超时
    })
  },

  // 下载文件
  downloadFile(filename) {
    return `${api.defaults.baseURL}/download/${filename}`
  },

  // 列出输出文件
  listFiles() {
    return api.get('/files')
  }
}

export default apiService