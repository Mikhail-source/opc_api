<template>
  <el-container style="height: 100vh; display: flex; flex-direction: column;">
    <el-header height="auto" style="padding: 12px 20px; background: #fff; border-bottom: 1px solid #eee;">
      <h2 style="margin: 0 0 8px 0; font-size: 18px;">⚙️ OPC Server Admin</h2>
      <ProjectBar />
    </el-header>
    
    <el-main style="padding: 20px; overflow: auto; flex: 1;">
      <TagTree />
    </el-main>
  </el-container>
</template>

<script setup>
import ProjectBar from './components/ProjectBar.vue'
import TagTree from './components/TagTree.vue'
import { useServerStore } from './stores/server'
import { useTagsStore } from './stores/tags'
import { watch } from 'vue'

const serverStore = useServerStore()
const tagsStore = useTagsStore()

// Авто-подключение WS при запуске сервера
watch(() => serverStore.running, (running) => {
  if (running) {
    tagsStore.connectWS()
  } else {
    tagsStore.disconnectWS()
  }
})
</script>

<style>
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; }
#app { height: 100vh; }
</style>
