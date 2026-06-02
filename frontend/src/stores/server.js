import { defineStore } from 'pinia'
import api from '../api'

export const useServerStore = defineStore('server', {
  state: () => ({
    running: false,
    loading: false
  }),
  actions: {
    async fetchStatus() {
      try {
        const res = await api.server.status()
        this.running = res.data.running
      } catch (e) {
        console.warn('⚠️ Не удалось получить статус сервера')
      }
    },
    async start() {
      this.loading = true
      try {
        await api.server.start()
        // Ждём инициализации (~1с)
        await new Promise(r => setTimeout(r, 1000))
        await this.fetchStatus()
      } finally {
        this.loading = false
      }
    },
    async stop() {
      this.loading = true
      try {
        await api.server.stop()
        this.running = false
      } finally {
        this.loading = false
      }
    }
  }
})
