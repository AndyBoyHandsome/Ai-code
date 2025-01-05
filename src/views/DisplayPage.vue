<template>
  <div class="display-container">
    <div class="page-header">
      <h1>分组展示</h1>
      <p class="subtitle">可视化展示分组结果</p>
    </div>

    <div class="display-layout">
      <!-- 过滤器侧边栏 -->
      <div class="filters-sidebar card">
        <div class="filter-section">
          <h3>视图模式</h3>
          <div class="view-options">
            <button 
              class="btn-option" 
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
              网格视图
            </button>
            <button 
              class="btn-option" 
              :class="{ active: viewMode === 'flow' }"
              @click="viewMode = 'flow'"
            >
              <i class="fas fa-stream"></i>
              流式视图
            </button>
          </div>
        </div>

        <div class="filter-section">
          <h3>分组筛选</h3>
          <div class="group-filters">
            <label 
              v-for="group in groups" 
              :key="group.id" 
              class="filter-item"
            >
              <input 
                type="checkbox" 
                v-model="selectedGroups" 
                :value="group.id"
              >
              <span class="filter-name">{{ group.name }}</span>
              <span class="filter-count">{{ group.images.length }}</span>
            </label>
          </div>
        </div>

        <div class="filter-section">
          <h3>排序方式</h3>
          <select v-model="sortBy" class="sort-select">
            <option value="name">名称</option>
            <option value="date">日期</option>
            <option value="size">大小</option>
          </select>
        </div>
      </div>

      <!-- 主内容区 -->
      <div class="display-content card">
        <div class="content-header">
          <div class="search-bar">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜索图片..."
            >
          </div>
          <div class="display-stats">
            显示 {{ filteredImages.length }} 张图片
          </div>
        </div>

        <div 
          class="images-container"
          :class="viewMode"
        >
          <div 
            v-for="image in filteredImages" 
            :key="image.id"
            class="image-card"
            @click="showImageDetail(image)"
          >
            <img :src="image.url" :alt="image.name">
            <div class="image-info">
              <div class="info-main">
                <span class="image-name">{{ image.name }}</span>
                <span class="image-group">{{ getGroupName(image.groupId) }}</span>
              </div>
              <div class="info-meta">
                <span class="image-date">{{ formatDate(image.date) }}</span>
                <span class="image-size">{{ formatSize(image.size) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

// 视图状态
const viewMode = ref<'grid' | 'flow'>('grid')
const searchQuery = ref('')
const sortBy = ref('name')
const selectedGroups = ref<number[]>([])

// 模拟数据
const groups = ref([
  { id: 1, name: '人像组 A', images: [1, 2] },
  { id: 2, name: '人像组 B', images: [3, 4] },
  { id: 3, name: '人像组 C', images: [5] }
])

interface Image {
  id: number
  url: string
  name: string
  groupId: number
  date: string
  size: number
}

const images = ref<Image[]>([
  {
    id: 1,
    url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500',
    name: 'Image 1',
    groupId: 1,
    date: '2024-01-01',
    size: 1024 * 1024
  },
  {
    id: 2,
    url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500',
    name: 'Image 2',
    groupId: 1,
    date: '2024-01-02',
    size: 2048 * 1024
  },
  {
    id: 3,
    url: 'https://images.unsplash.com/photo-1554151228-14d9def656e4?w=500',
    name: 'Image 3',
    groupId: 2,
    date: '2024-01-03',
    size: 1536 * 1024
  },
  {
    id: 4,
    url: 'https://images.unsplash.com/photo-1547624643-3bf761b09502?w=500',
    name: 'Image 4',
    groupId: 2,
    date: '2024-01-04',
    size: 3072 * 1024
  },
  {
    id: 5,
    url: 'https://images.unsplash.com/photo-1546538994-4f15d0aa966f?w=500',
    name: 'Image 5',
    groupId: 3,
    date: '2024-01-05',
    size: 1024 * 768
  }
  // ... 更多图片数据
])

// 计算属性
const filteredImages = computed(() => {
  let result = images.value

  // 搜索过滤
  if (searchQuery.value) {
    result = result.filter(img => 
      img.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // 分组过滤
  if (selectedGroups.value.length > 0) {
    result = result.filter(img => 
      selectedGroups.value.includes(img.groupId)
    )
  }

  // 排序
  result = [...result].sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'date':
        return new Date(b.date).getTime() - new Date(a.date).getTime()
      case 'size':
        return b.size - a.size
      default:
        return 0
    }
  })

  return result
})

// 工具方法
const getGroupName = (groupId: number): string => {
  const group = groups.value.find(g => g.id === groupId)
  return group ? group.name : ''
}

const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`
}

const showImageDetail = (image: Image) => {
  // TODO: 实现图片详情展示逻辑
  console.log('Show image detail:', image)
}
</script>

<style scoped>
.display-container {
  padding: 2rem;
}

.display-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.filters-sidebar {
  height: fit-content;
}

.filter-section {
  padding: 1.5rem;
  border-bottom: 1px solid var(--background-color);
}

.filter-section:last-child {
  border-bottom: none;
}

.filter-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.view-options {
  display: flex;
  gap: 1rem;
}

.btn-option {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: var(--background-color);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.btn-option.active {
  background: var(--primary-color);
  color: white;
}

.group-filters {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.filter-count {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.sort-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--background-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
  color: var(--text-primary);
}

.display-content {
  min-height: calc(100vh - 200px);
}

.content-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--background-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.display-stats {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.images-container {
  padding: 1.5rem;
  display: grid;
  gap: 1.5rem;
}

.images-container.grid {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}

.images-container.flow {
  grid-template-columns: 1fr;
}

.image-card {
  border-radius: var(--border-radius);
  overflow: hidden;
  background: var(--background-color);
  cursor: pointer;
  transition: var(--transition);
}

.image-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--box-shadow);
}

.image-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.image-info {
  padding: 1rem;
}

.info-main {
  margin-bottom: 0.5rem;
}

.image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.image-group {
  font-size: 0.9rem;
  color: var(--primary-color);
}

.info-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .display-layout {
    grid-template-columns: 1fr;
  }
}
</style> 