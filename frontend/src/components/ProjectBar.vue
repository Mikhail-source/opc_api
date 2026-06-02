<template>
  <el-card shadow="never" class="project-bar">
    <div class="toolbar">
      <!-- Управление сервером -->
      <el-button 
        :type="serverStore.running ? 'danger' : 'success'" 
        @click="serverStore.running ? serverStore.stop() : serverStore.start()"
        :loading="serverStore.loading"
      >
        {{ serverStore.running ? '⏹️ Остановить' : '▶️ Запустить' }}
      </el-button>

      <el-divider direction="vertical" />

      <!-- Выбор проекта -->
      <el-select 
        v-model="selectedProject" 
        placeholder="Выберите проект" 
        style="width: 220px" 
        @change="loadProject"
      >
        <el-option v-for="p in projects" :key="p" :label="p" :value="p" />
      </el-select>
      <el-button @click="refreshProjects" :loading="loadingList">🔄 Обновить</el-button>

      <el-divider direction="vertical" />

      <!-- Статусы -->
      <el-tag :type="tagsStore.wsStatus === 'connected' ? 'success' : 'info'" effect="dark" size="small">
        {{ tagsStore.wsStatus === 'connected' ? '🟢 Online' : '⚪ Offline' }}
      </el-tag>
      <el-tag type="info" effect="plain" size="small">
        {{ projectStatus.tags_count || 0 }} тегов
      </el-tag>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useServerStore } from '../stores/server'
import { useTagsStore } from '../stores/tags'
import api from '../api'
import { ElMessage } from 'element-plus'

const serverStore = useServerStore()
const tagsStore = useTagsStore()
const projects = ref([])
const selectedProject = ref('')
const projectStatus = ref({})
const loadingList = ref(false)

onMounted(async () => {
  await serverStore.fetchStatus()
  await refreshProjects()
  await refreshStatus()
  await tagsStore.fetchTags()
  // Подключаем WebSocket только если сервер уже запущен
  if (serverStore.running) {
    tagsStore.connectWS()
  }
})

const refreshProjects = async () => {
  loadingList.value = true
  try {
    const res = await api.projects.list()
    projects.value = res.data
  } finally {
    loadingList.value = false
  }
}

const loadProject = async (path) => {
  if (!path) return
  try {
    await api.projects.load(path)
    await refreshStatus()
    await tagsStore.fetchTags()
    ElMessage.success(`Проект "${path}" загружен`)
  } catch {
    ElMessage.error('Ошибка загрузки проекта')
  }
}

const refreshStatus = async () => {
  const res = await api.projects.status()
  projectStatus.value = res.data
}
</script>

<style scoped>
.project-bar { margin-bottom: 16px; }
.toolbar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
</style>
