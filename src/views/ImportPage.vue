<template>
  <div class="import-container">
    <div class="page-header">
      <h1>图片导入</h1>
      <p class="subtitle">支持批量导入图片文件，智能处理分类</p>
    </div>

    <div class="upload-section card">
      <div 
        class="upload-area" 
        @drop.prevent="handleDrop" 
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        :class="{ 'drag-over': isDragOver }"
      >
        <input 
          type="file" 
          ref="fileInput" 
          multiple 
          accept="image/*" 
          @change="handleFileSelect" 
          class="file-input"
        >
        <div class="upload-content" @click="triggerFileInput">
          <i class="fas fa-cloud-upload-alt"></i>
          <h3>拖拽文件到此处或点击上传</h3>
          <p class="upload-hint">
            支持 JPG、PNG 格式
            <br>单次最多可上传 1000 张图片
            <br>单张图片大小不超过 5MB
          </p>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-if="isUploading" class="progress-section card">
      <div class="progress-header">
        <h3>上传进度</h3>
        <div class="progress-stats">
          <span class="stat">
            <i class="fas fa-check"></i>
            已上传: {{ uploadedCount }} / {{ totalFiles }}
          </span>
          <span class="stat error">
            <i class="fas fa-times"></i>
            失败: {{ failedCount }}
          </span>
        </div>
      </div>
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progress + '%' }">
          <span class="progress-text">{{ progress }}%</span>
        </div>
      </div>
    </div>

    <!-- 预览区域 -->
    <div v-if="previewImages.length > 0" class="preview-section card">
      <div class="preview-header">
        <h3>图片预览</h3>
        <span class="preview-count">{{ previewImages.length }} 张图片</span>
      </div>
      <div class="preview-grid">
        <div 
          v-for="image in previewImages" 
          :key="image.id" 
          class="preview-item"
          @click="showImageDetail(image)"
        >
          <img :src="image.url" :alt="image.name">
          <div class="preview-info">
            <span class="preview-name">{{ image.name }}</span>
            <span class="preview-size">{{ formatFileSize(image.size) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 失败列表 -->
    <div v-if="failedFiles.length > 0" class="failed-section card">
      <h3>上传失败列表</h3>
      <div class="failed-list">
        <div v-for="(file, index) in failedFiles" :key="index" class="failed-item">
          <i class="fas fa-exclamation-circle"></i>
          <span class="failed-name">{{ file.name }}</span>
          <span class="failed-reason">{{ file.reason }}</span>
        </div>
      </div>
    </div>

    <!-- 图片详情弹窗 -->
    <div v-if="selectedImage" class="modal" @click="selectedImage = null">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="selectedImage = null">
          <i class="fas fa-times"></i>
        </button>
        <img :src="selectedImage.url" :alt="selectedImage.name">
        <div class="modal-info">
          <h4>{{ selectedImage.name }}</h4>
          <p>大小：{{ formatFileSize(selectedImage.size) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileInput = ref(null)
const isUploading = ref(false)
const progress = ref(0)
const uploadedCount = ref(0)
const totalFiles = ref(0)
const failedCount = ref(0)
const failedFiles = ref([])
const showResult = ref(false)
const previewImages = ref([])
const isDragOver = ref(false)
const selectedImage = ref(null)

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  processFiles(files)
}

const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  processFiles(files)
}

const processFiles = async (files) => {
  if (files.length > 1000) {
    alert('一次最多只能上传1000张图片')
    return
  }

  isUploading.value = true
  progress.value = 0
  uploadedCount.value = 0
  failedCount.value = 0
  failedFiles.value = []
  totalFiles.value = files.length
  showResult.value = false
  previewImages.value = []

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    
    // 检查文件类型和大小
    if (!file.type.startsWith('image/')) {
      failedFiles.value.push({
        name: file.name,
        reason: '不支持的文件格式'
      })
      failedCount.value++
      continue
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB限制
      failedFiles.value.push({
        name: file.name,
        reason: '文件大小超过5MB'
      })
      failedCount.value++
      continue
    }

    try {
      // 创建预览
      const reader = new FileReader()
      reader.onload = (e) => {
        previewImages.value.push({
          id: i,
          url: e.target.result,
          name: file.name
        })
      }
      reader.readAsDataURL(file)

      // 模拟上传过程
      await new Promise(resolve => setTimeout(resolve, 100))
      uploadedCount.value++
    } catch (error) {
      failedFiles.value.push({
        name: file.name,
        reason: '上传失败: ' + error.message
      })
      failedCount.value++
    }

    progress.value = Math.round((i + 1) * 100 / files.length)
  }

  showResult.value = true
  isUploading.value = false
}

const handleDragOver = () => {
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const showImageDetail = (image) => {
  selectedImage.value = image
}

const formatFileSize = (size) => {
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(2) + ' KB'
  return (size / (1024 * 1024)).toFixed(2) + ' MB'
}
</script>

<style scoped>
.import-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.upload-section {
  margin-bottom: 2rem;
}

.upload-area {
  border: 2px dashed #e1e1e1;
  border-radius: var(--border-radius);
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: var(--transition);
}

.upload-area.drag-over {
  border-color: var(--primary-color);
  background-color: rgba(0, 168, 255, 0.05);
}

.upload-content i {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.upload-hint {
  color: var(--text-secondary);
  margin-top: 1rem;
  line-height: 1.6;
}

.file-input {
  display: none;
}

.progress-section {
  margin-bottom: 2rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-stats {
  display: flex;
  gap: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat.error {
  color: var(--error-color);
}

.progress-bar-container {
  background-color: #f1f2f6;
  border-radius: 100px;
  height: 20px;
  overflow: hidden;
}

.progress-bar {
  background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
  height: 100%;
  transition: width 0.3s ease;
  position: relative;
}

.progress-text {
  position: absolute;
  right: 10px;
  color: white;
  font-size: 0.8rem;
  line-height: 20px;
}

.preview-section {
  margin-bottom: 2rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.preview-count {
  color: var(--text-secondary);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.preview-item {
  position: relative;
  border-radius: var(--border-radius);
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition);
}

.preview-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--box-shadow);
}

.preview-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.preview-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
}

.preview-name {
  display: block;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-size {
  font-size: 0.8rem;
  opacity: 0.8;
}

.failed-section {
  margin-bottom: 2rem;
}

.failed-list {
  max-height: 300px;
  overflow-y: auto;
}

.failed-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}

.failed-item i {
  color: var(--error-color);
}

.failed-reason {
  color: var(--error-color);
  margin-left: auto;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 1rem;
  border-radius: var(--border-radius);
  max-width: 90vw;
  max-height: 90vh;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  z-index: 1;
}

.modal-info {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: var(--border-radius);
  margin-top: 1rem;
}
</style> 