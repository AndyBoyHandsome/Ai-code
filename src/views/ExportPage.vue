<template>
  <div class="export-container">
    <div class="page-header">
      <h1>导出分组</h1>
      <p class="subtitle">将分组结果导出为多种格式</p>
    </div>

    <div class="export-layout">
      <!-- 左侧选项面板 -->
      <div class="options-panel card">
        <div class="option-section">
          <h3>选择分组</h3>
          <div class="group-list">
            <label class="group-item select-all">
              <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" />
              <span class="group-name">全选</span>
              <span class="group-count">({{ groups.length }}个分组)</span>
            </label>
            <label v-for="group in groups" :key="group.id" class="group-item">
              <input type="checkbox" v-model="selectedGroups" :value="group.id" />
              <span class="group-name">{{ group.name }}</span>
              <span class="group-count">({{ group.images.length }}张)</span>
            </label>
          </div>
        </div>

        <div class="option-section">
          <h3>导出选项</h3>
          <div class="export-options">
            <div class="option-item">
              <label>导出格式</label>
              <select v-model="exportFormat" class="select-input">
                <option value="zip">ZIP压缩包</option>
                <option value="folder">文件夹</option>
                <option value="json">JSON文件</option>
              </select>
            </div>

            <div class="option-item">
              <label>图片质量</label>
              <select v-model="imageQuality" class="select-input">
                <option value="original">原始质量</option>
                <option value="high">高质量</option>
                <option value="medium">中等质量</option>
                <option value="low">低质量</option>
              </select>
            </div>

            <div class="option-item">
              <label>命名规则</label>
              <select v-model="namingRule" class="select-input">
                <option value="original">原始文件名</option>
                <option value="index">序号命名</option>
                <option value="date">日期命名</option>
              </select>
            </div>
          </div>
        </div>

        <div class="option-section">
          <h3>导出预览</h3>
          <div class="export-preview">
            <div class="preview-info">
              <div class="info-item">
                <span class="label">选中分组：</span>
                <span class="value">{{ selectedGroups.length }}个</span>
              </div>
              <div class="info-item">
                <span class="label">图片总数：</span>
                <span class="value">{{ totalImages }}张</span>
              </div>
              <div class="info-item">
                <span class="label">预计大小：</span>
                <span class="value">{{ estimatedSize }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="btn btn-primary" @click="startExport" :disabled="!canExport">
            <i class="fas fa-file-export"></i>
            开始导出
          </button>
        </div>
      </div>

      <!-- 右侧预览面板 -->
      <div class="preview-panel card">
        <div class="preview-header">
          <h3>导出内容预览</h3>
          <div class="preview-controls">
            <button
              class="btn-icon"
              :class="{ active: previewMode === 'grid' }"
              @click="previewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <button
              class="btn-icon"
              :class="{ active: previewMode === 'list' }"
              @click="previewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>

        <div class="preview-content" :class="previewMode">
          <div v-for="group in selectedGroupsData" :key="group.id" class="preview-group">
            <div class="group-header">
              <h4>{{ group.name }}</h4>
              <span class="count">{{ group.images.length }}张</span>
            </div>
            <div class="group-images">
              <div v-for="image in group.images" :key="image.id" class="preview-image">
                <img :src="image.url" :alt="image.name" />
                <div class="image-info">
                  <span class="image-name">{{ getExportName(image) }}</span>
                  <span class="image-size">{{ formatSize(image.size) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="[toast.show && 'show', `toast-${toast.type}`]">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGroupStore } from '@/stores/group'
import { useImageStore } from '@/stores/image'
import { useApiStore } from '@/stores/api'

interface Image {
  id: string | number
  url: string
  name: string
  groupId: string | number | null
  size: number
  type?: string
  path?: string
  createdAt?: string
}

interface Group {
  id: string | number
  name: string
  description?: string
  images: Image[]
  createdAt?: string
  updatedAt?: string
}

interface Toast {
  show: boolean
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
}

// 状态
const selectedGroups = ref<(string | number)[]>([])
const exportFormat = ref<'zip' | 'folder' | 'json'>('zip')
const imageQuality = ref<'original' | 'high' | 'medium' | 'low'>('original')
const namingRule = ref<'original' | 'index' | 'date'>('original')
const previewMode = ref<'grid' | 'list'>('grid')
const exportPath = ref<FileSystemDirectoryHandle | null>(null)
const isExporting = ref(false)
const exportProgress = ref(0)
const failedExports = ref<Array<{ name: string; error: string }>>([])

// Store 实例
const groupStore = useGroupStore()
const imageStore = useImageStore()
const apiStore = useApiStore()

const groups = computed<Group[]>(() => {
  return groupStore.groups.map((group) => ({
    ...group,
    images: imageStore.getImagesByGroupId(group.id),
  }))
})

// 计算属性
const selectedGroupsData = computed(() => {
  return groups.value.filter((group) => selectedGroups.value.includes(group.id))
})

const totalImages = computed(() => {
  return selectedGroupsData.value.reduce((sum, group) => sum + group.images.length, 0)
})

const estimatedSize = computed(() => {
  const totalBytes = selectedGroupsData.value.reduce((sum, group) => {
    return sum + group.images.reduce((groupSum, img) => groupSum + img.size, 0)
  }, 0)
  return formatSize(totalBytes)
})

const canExport = computed(() => selectedGroups.value.length > 0)

// 方法
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

const getExportName = (image: Image): string => {
  switch (namingRule.value) {
    case 'index':
      return `image_${image.id}`
    case 'date':
      return `image_${new Date().toISOString().split('T')[0]}_${image.id}`
    default:
      return image.name
  }
}

const selectExportDirectory = async () => {
  try {
    // 检查 showDirectoryPicker API 是否可用
    if (!('showDirectoryPicker' in window)) {
      showToast('您的浏览器不支持文件夹选择功能，请使用最新版本的 Chrome 或 Edge 浏览器', 'error')
      return
    }

    const handle = await window
      .showDirectoryPicker({
        mode: 'readwrite',
        startIn: 'downloads',
      })
      .catch((error) => {
        if (error.name === 'AbortError') {
          // 用户取消了选择
          return null
        }
        throw error
      })

    if (!handle) return

    // 验证权限
    const permissionStatus = await handle.queryPermission({ mode: 'readwrite' })
    if (permissionStatus === 'granted') {
      exportPath.value = handle
      return true
    }

    // 请求权限
    const requestPermission = await handle.requestPermission({ mode: 'readwrite' })
    if (requestPermission === 'granted') {
      exportPath.value = handle
      return true
    } else {
      showToast('需要文件夹访问权限才能导出图片', 'error')
      return false
    }
  } catch (error) {
    console.error('选择导出文件夹失败:', error)
    if (error.name === 'SecurityError') {
      showToast('没有权限访问文件系统，请检查浏览器设置', 'error')
    } else {
      showToast('选择导出文件夹失败：' + error.message, 'error')
    }
    return false
  }
}

const startExport = async () => {
  if (!selectedGroups.value.length) {
    showToast('请先选择要导出的图片', 'warning')
    return
  }

  if (!exportPath.value) {
    const success = await selectExportDirectory()
    if (!success) return
  }

  try {
    isExporting.value = true
    exportProgress.value = 0

    // 创建导出目录
    const exportDir = exportPath.value
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const dirName = `exported-images-${timestamp}`

    const newDir = await exportDir
      .getDirectoryHandle(dirName, { create: true })
      .catch(async (error) => {
        if (error.name === 'TypeMismatchError') {
          // 目录已存在，尝试使用新名称
          return await exportDir.getDirectoryHandle(`${dirName}-${Date.now()}`, { create: true })
        }
        throw error
      })

    const total = selectedGroups.value.length
    let processed = 0

    // 并行导出图片，但限制并发数
    const concurrency = 3
    const chunks = []
    for (let i = 0; i < selectedGroups.value.length; i += concurrency) {
      chunks.push(selectedGroups.value.slice(i, i + concurrency))
    }

    for (const chunk of chunks) {
      await Promise.all(
        chunk.map(async (groupId) => {
          const group = groupStore.getGroupById(groupId)
          if (!group) return

          const images = imageStore.getImagesByGroupId(groupId)
          if (!images.length) return

          try {
            // 创建导出目录
            const groupDir = await newDir.getDirectoryHandle(group.name, { create: true })

            // 导出图片
            for (const image of images) {
              try {
                // 获取图片数据
                const response = await fetch(image.url)
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
                const blob = await response.blob()

                // 创建文件
                const fileHandle = await groupDir.getFileHandle(image.name, { create: true })
                const writable = await fileHandle.createWritable()
                await writable.write(blob)
                await writable.close()

                processed++
                exportProgress.value = Math.round((processed / total) * 100)
              } catch (error) {
                console.error(`导出图片 ${image.name} 失败:`, error)
                failedExports.value.push({
                  name: image.name,
                  error: error.message,
                })
              }
            }
          } catch (error) {
            console.error(`导出分组 ${group.name} 失败:`, error)
            failedExports.value.push({
              name: group.name,
              error: error.message,
            })
          }
        }),
      )
    }

    if (failedExports.value.length) {
      showToast(`导出完成，但有 ${failedExports.value.length} 个文件失败`, 'warning')
    } else {
      showToast('导出成功')
    }
  } catch (error) {
    console.error('导出失败:', error)
    if (error.name === 'NotAllowedError') {
      showToast('没有权限访问选择的文件夹，请重新选择', 'error')
    } else {
      showToast('导出失败：' + error.message, 'error')
    }
  } finally {
    isExporting.value = false
    exportProgress.value = 0
  }
}

// Toast 功能
const toast = ref<Toast>({
  show: false,
  message: '',
  type: 'info',
})

const showToast = (message: string, type: Toast['type'] = 'success') => {
  toast.value = {
    show: true,
    message,
    type,
  }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 添加 FileSystemDirectoryHandle 类型声明
declare global {
  interface Window {
    showDirectoryPicker(options?: {
      mode?: 'read' | 'readwrite'
      startIn?: 'desktop' | 'documents' | 'downloads' | 'music' | 'pictures' | 'videos'
    }): Promise<FileSystemDirectoryHandle>
  }
}

interface FileSystemDirectoryHandle {
  kind: 'directory'
  name: string
  queryPermission(descriptor: { mode: 'read' | 'readwrite' }): Promise<PermissionState>
  requestPermission(descriptor: { mode: 'read' | 'readwrite' }): Promise<PermissionState>
  getDirectoryHandle(
    name: string,
    options?: { create?: boolean },
  ): Promise<FileSystemDirectoryHandle>
  getFileHandle(name: string, options?: { create?: boolean }): Promise<FileSystemFileHandle>
  values(): AsyncIterableIterator<FileSystemHandle>
}

interface FileSystemFileHandle {
  kind: 'file'
  name: string
  getFile(): Promise<File>
  createWritable(): Promise<FileSystemWritableFileStream>
}

interface FileSystemWritableFileStream extends WritableStream {
  write(data: BufferSource | Blob | string): Promise<void>
  seek(position: number): Promise<void>
  truncate(size: number): Promise<void>
}

// 添加全选功能
const isAllSelected = computed(() => {
  return selectedGroups.value.length === groups.value.length
})

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedGroups.value = []
  } else {
    selectedGroups.value = groups.value.map((group) => group.id)
  }
}
</script>

<style scoped>
.export-container {
  padding: 2rem;
}

.export-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.options-panel {
  height: fit-content;
}

.option-section {
  padding: 1.5rem;
  border-bottom: 1px solid var(--background-color);
}

.option-section:last-child {
  border-bottom: none;
}

.option-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.group-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.group-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.group-item:hover {
  background: var(--background-color);
}

.group-name {
  flex: 1;
  font-weight: 500;
}

.group-count {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.option-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.option-item label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.select-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--background-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
  color: var(--text-primary);
}

.preview-info {
  background: var(--background-color);
  padding: 1rem;
  border-radius: var(--border-radius);
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item .label {
  color: var(--text-secondary);
}

.actions {
  padding: 1.5rem;
  display: flex;
  justify-content: center;
}

.preview-panel {
  min-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--background-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.preview-group {
  margin-bottom: 2rem;
}

.preview-group:last-child {
  margin-bottom: 0;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.group-header h4 {
  margin: 0;
  color: var(--text-primary);
}

.group-images {
  display: grid;
  gap: 1rem;
}

.preview-content.grid .group-images {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

.preview-content.list .group-images {
  grid-template-columns: 1fr;
}

.preview-image {
  border-radius: var(--border-radius);
  overflow: hidden;
  background: var(--background-color);
}

.preview-image img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.image-info {
  padding: 0.75rem;
}

.image-name {
  display: block;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.image-size {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .export-layout {
    grid-template-columns: 1fr;
  }
}

/* Toast 样式 */
.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: var(--border-radius);
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  color: var(--text-primary);
  font-size: 0.875rem;
  z-index: 2000;
  opacity: 0;
  transform: translateY(-20px);
  transition: all 0.3s ease;
}

.toast.show {
  opacity: 1;
  transform: translateY(0);
}

.toast.toast-success {
  background: var(--success-color);
  color: white;
}

.toast.toast-error {
  background: var(--error-color);
  color: white;
}

.toast.toast-warning {
  background: var(--warning-color);
  color: white;
}

.select-all {
  padding: 0.75rem;
  background: rgba(0, 168, 255, 0.1);
  border-radius: var(--border-radius);
  margin-bottom: 1rem;
  font-weight: 500;
}

.select-all:hover {
  background: rgba(0, 168, 255, 0.15);
}

input[type='checkbox'] {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid var(--primary-color);
  appearance: none;
  cursor: pointer;
  position: relative;
  transition: var(--transition);
}

input[type='checkbox']:checked {
  background-color: var(--primary-color);
}

input[type='checkbox']:checked::after {
  content: '✓';
  color: white;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
}

input[type='checkbox']:hover {
  border-color: var(--accent-color);
}

input[type='checkbox']:checked:hover {
  background-color: var(--accent-color);
}
</style>
