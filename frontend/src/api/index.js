import axios from 'axios'

const api = axios.create({
  baseURL: '', // Пусто, т.к. прокси Vite сам перенаправит /api и /ws
  timeout: 5000
})

// Интерцептор для отладки
api.interceptors.request.use(config => {
  console.log(`📡 [API] ${config.method?.toUpperCase()} ${config.url}`)
  return config
})
api.interceptors.response.use(
  res => res,
  err => {
    console.error(`❌ [API Error] ${err.config?.url} → ${err.response?.status || 'NO RESPONSE'}`)
    return Promise.reject(err)
  }
)

export default {
  projects: {
    list: () => api.get('/api/projects'),
    load: (path) => api.post('/api/projects/load', null, { params: { path } }),
    save: () => api.post('/api/projects/save'),
    status: () => api.get('/api/projects/status')
  },
  server: {
    status: () => api.get('/api/server/status'),
    start: () => api.post('/api/server/start'),
    stop: () => api.post('/api/server/stop')
  },
  tags: {
    list: () => api.get('/api/tags')
  }
}
