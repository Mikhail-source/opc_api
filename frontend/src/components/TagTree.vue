<template>
  <el-card shadow="never">
    <template #header>
      <div class="tree-header">
        <h3>📁 Теги</h3>
        <el-input v-model="search" placeholder="Поиск..." clearable style="width: 180px" />
      </div>
    </template>
    
    <el-tree
      :data="treeData"
      :props="{ label: 'name', children: 'children' }"
      node-key="id"
      default-expand-all
      :filter-node-method="filterNode"
      ref="treeRef"
    >
      <template #default="{ node, data }">
        <span class="tag-node">
          <span v-if="data.isTag" :class="['quality-dot', data.quality?.toLowerCase()]"></span>
          <span class="tag-name">{{ data.name }}</span>
          <span v-if="data.isTag" class="tag-value">{{ formatValue(data) }}</span>
        </span>
      </template>
    </el-tree>
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useTagsStore } from '../stores/tags'

const tagsStore = useTagsStore()
const search = ref('')
const treeRef = ref()

// Преобразуем плоский список тегов в дерево по путям
const treeData = computed(() => {
  const root = { id: 'root', name: 'Теги', children: [] }
  
  for (const tag of tagsStore.tagArray) {
    const path = tag.path || 'Без группы'
    const parts = path.split('/').filter(Boolean)
    
    let current = root.children
    parts.forEach((p, i) => {
      let found = current.find(c => c.name === p)
      if (!found) {
        found = { id: `folder_${i}_${p}`, name: p, children: [] }
        current.push(found)
      }
      current = found.children
    })
    
    // Добавляем сам тег
    current.push({
      id: `tag_${tag.name}`,
      name: tag.name,
      isTag: true,
      ...tag
    })
  }
  return root.children
})

const filterNode = (value, data) => {
  if (!value) return true
  return data.name?.includes(value) || data.path?.includes(value)
}

watch(search, (val) => treeRef.value?.filter(val))

const formatValue = (tag) => {
  if (tag.value === null || tag.value === undefined) return '---'
  if (typeof tag.value === 'number') return tag.value.toFixed(3)
  return String(tag.value)
}
</script>

<style scoped>
.tree-header { display: flex; justify-content: space-between; align-items: center; }
.tag-node { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.tag-name { flex: 1; }
.tag-value { color: #666; font-family: monospace; min-width: 80px; text-align: right; }
.quality-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.quality-dot.good { background: #67C23A; }
.quality-dot.bad { background: #F56C6C; }
.quality-dot.unknown { background: #909399; }
</style>
