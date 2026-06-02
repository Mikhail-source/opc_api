import { defineStore } from 'pinia'
import api from '../api'

export const useTagsStore = defineStore('tags', {
  state: () => ({
    tags: {},
    wsStatus: 'disconnected', // 'disconnected' | 'connecting' | 'connected'
    ws: null
  }),
  getters: {
    tagArray: (state) => Object.values(state.tags),
    tagsByPath: (state) => {
      const tree = {}
      for (const tag of Object.values(state.tags)) {
        const path = tag.path || 'Без группы'
        if (!tree[path]) tree[path] = []
        tree[path].push(tag)
      }
      return tree
    }
  },
  actions: {
    async fetchTags() {
      try {
        const res = await api.tags.list()
        this.tags = res.data
      } catch (e) {
        console.warn('⚠️ Не удалось загрузить теги')
      }
    },
    connectWS() {
      if (this.ws) this.ws.close()
      
      const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
      const url = `${protocol}//${location.host}/ws/tags`
      
      console.log(`🔌 Connecting to ${url}`)
      this.wsStatus = 'connecting'
      this.ws = new WebSocket(url)
      
      this.ws.onopen = () => {
        console.log('✅ WebSocket connected')
        this.wsStatus = 'connected'
      }
      
      this.ws.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if (msg.type === 'snapshot') {
          // Начальный снапшот: заменяем всё
          this.tags = msg.payload
        } else if (msg.type === 'update') {
          // Дельта-обновление: только изменившийся тег
          const { name, ...data } = msg.payload
          if (this.tags[name]) {
            this.tags[name] = { ...this.tags[name], ...data }
          }
        }
      }
      
      this.ws.onclose = () => {
        console.log('❌ WebSocket disconnected')
        this.wsStatus = 'disconnected'
        // Авто-реконнект через 3 сек
        setTimeout(() => {
          if (this.wsStatus !== 'connected') this.connectWS()
        }, 3000)
      }
      
      this.ws.onerror = (err) => {
        console.error('❌ WebSocket error:', err)
        this.wsStatus = 'disconnected'
      }
    },
    disconnectWS() {
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
      this.wsStatus = 'disconnected'
    }
  }
})
