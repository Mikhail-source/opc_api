<template>
  <el-card shadow="never" class="script-editor">
    <template #header>
      <div class="editor-header">
        <h3>📝 Lua Script</h3>
        <div class="actions">
          <el-button @click="loadScript" :loading="loading">📥 Load</el-button>
          <el-button type="primary" @click="applyScript" :loading="applying">🚀 Apply</el-button>
        </div>
      </div>
    </template>
    <el-input
      v-model="scriptContent"
      type="textarea"
      :rows="10"
      placeholder="Lua code...&#10;local v = tag_get('Temp')&#10;if v > 80 then tag_set('Alarm', true) end"
      style="font-family: 'Consolas', monospace; font-size: 13px;"
    />
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const scriptContent = ref('')
const loading = ref(false)
const applying = ref(false)

const loadScript = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/script/content')
    scriptContent.value = res.data.content || ''
    ElMessage.success('Script loaded')
  } catch { ElMessage.error('Failed to load script') }
  finally { loading.value = false }
}

const applyScript = async () => {
  applying.value = true
  try {
    await axios.post('/api/script/reload', { content: scriptContent.value, interval: 1.0 })
    ElMessage.success('Script applied & hot-reloaded')
  } catch { ElMessage.error('Failed to apply script') }
  finally { applying.value = false }
}
</script>

<style scoped>
.editor-header { display: flex; justify-content: space-between; align-items: center; }
</style>
