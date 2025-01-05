<template>
  <div class="grouping-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1>智能分组</h1>
        <p class="subtitle">共 {{ totalImages }} 张图片，{{ groups.length }} 个分组</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-text" @click="toggleSelectionMode" :class="{ active: isSelecting }">
          <i class="fas" :class="isSelecting ? 'fa-times' : 'fa-check-square'"></i>
          {{ isSelecting ? '退出选择' : '批量选择' }}
        </button>
        <button
          class="btn btn-primary"
          @click="showAutoGroupSettings"
          :disabled="isProcessing || !hasImages"
        >
          <i class="fas fa-brain"></i>
          {{ isProcessing ? '处理中...' : '开始智能分组' }}
        </button>
        <button class="btn btn-outline" @click="showImportDialog = true">
          <i class="fas fa-file-import"></i>
          导入图片
        </button>
      </div>
    </header>

    <!-- 进度条 -->
    <div v-if="isProcessing" class="progress-bar">
      <div class="progress-info">
        <span>{{ groupingStatus.currentStep }}</span>
        <span>{{ groupingStatus.processedImages }}/{{ groupingStatus.totalImages }}</span>
      </div>
      <div class="progress-inner" :style="{ width: `${groupingStatus.currentProgress}%` }">
        <span class="progress-text"> {{ groupingStatus.currentProgress }}% </span>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧分组列表 -->
      <aside class="group-sidebar">
        <div class="group-header">
          <h2>分组列表</h2>
          <div class="group-actions">
            <button class="btn btn-sm" @click="createGroup">
              <i class="fas fa-plus"></i>
              新建分组
            </button>
            <button
              class="btn btn-sm"
              :disabled="!selectedImages.length"
              @click="createGroupFromSelection"
            >
              <i class="fas fa-object-group"></i>
              从选中创建
            </button>
          </div>
        </div>
        <div class="group-toolbar">
          <div class="search-bar">
            <i class="fas fa-search"></i>
            <input type="text" v-model="groupSearchQuery" placeholder="搜索分组..." />
          </div>
          <div class="sort-controls">
            <select v-model="groupSortBy" class="sort-select">
              <option value="name">按名称</option>
              <option value="createdAt">按创建时间</option>
              <option value="count">按图片数量</option>
            </select>
            <button
              class="btn-icon"
              @click="toggleGroupSortOrder"
              :title="groupSortOrder === 'asc' ? '升序' : '降序'"
            >
              <i
                class="fas"
                :class="groupSortOrder === 'asc' ? 'fa-sort-amount-down' : 'fa-sort-amount-up'"
              ></i>
            </button>
          </div>
        </div>
        <div class="group-list">
          <!-- 未分组项 -->
          <div class="group-item" :class="{ active: !selectedGroup }" @click="selectGroup(null)">
            <span class="group-name">
              <i class="fas fa-folder"></i>
              未分组
            </span>
            <span class="group-count">{{ ungroupedCount }}</span>
          </div>
          <!-- 分组列表 -->
          <div
            v-for="group in filteredGroups"
            :key="group.id"
            class="group-item"
            :class="{
              active: selectedGroup?.id === group.id,
              'drag-over': dragOverGroup === group.id,
            }"
            @click="selectGroup(group)"
            @dragover.prevent="handleDragOver($event, group)"
            @dragleave="handleDragLeave(group)"
            @drop.prevent="handleDrop($event, group)"
          >
            <span class="group-name">
              <i class="fas fa-folder-open"></i>
              {{ group.name }}
            </span>
            <span class="group-count">{{ getGroupImageCount(group) }}</span>
            <div class="group-actions">
              <button class="btn-icon" @click.stop="editGroup(group)">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn-icon" @click.stop="deleteGroup(group.id)">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧图片区域 -->
      <main class="image-content">
        <div class="toolbar">
          <div class="search-bar">
            <i class="fas fa-search"></i>
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索图片..."
              :class="{ searching: isSearching }"
            />
            <i v-if="searchQuery" class="fas fa-times clear-search" @click="searchQuery = ''"></i>
            <i v-if="isSearching" class="fas fa-spinner fa-spin"></i>
          </div>
          <div class="view-controls">
            <div v-if="isSelecting" class="selection-controls">
              <button class="btn btn-text" @click="selectAll" :disabled="!filteredImages.length">
                <i class="fas fa-check-double"></i>
                全选
              </button>
              <button class="btn btn-text" @click="deselectAll" :disabled="!selectedImages.length">
                <i class="fas fa-times"></i>
                取消选择
              </button>
              <button
                class="btn btn-text"
                @click="invertSelection"
                :disabled="!filteredImages.length"
              >
                <i class="fas fa-random"></i>
                反选
              </button>
              <div class="selection-info">已选择 {{ selectedImages.length }} 张图片</div>
            </div>
            <div class="filter-controls">
              <div class="filter-group">
                <button
                  v-for="filter in filterTypes"
                  :key="filter.value"
                  class="btn-text"
                  :class="{ active: filterType === filter.value }"
                  @click="filterType = filter.value"
                >
                  {{ filter.label }}
                </button>
              </div>
              <select v-model="sortBy">
                <option value="name">按名称</option>
                <option value="size">按大小</option>
                <option value="createdAt">按时间</option>
                <option value="group">按分组</option>
              </select>
              <button
                class="btn-icon"
                @click="toggleSortOrder"
                :title="sortOrder === 'asc' ? '升序' : '降序'"
              >
                <i
                  class="fas"
                  :class="sortOrder === 'asc' ? 'fa-sort-amount-down' : 'fa-sort-amount-up'"
                ></i>
              </button>
            </div>
            <div class="size-control">
              <button class="btn-icon" @click="decreaseImageSize" :disabled="imageSize <= 100">
                <i class="fas fa-search-minus"></i>
              </button>
              <span class="size-value">{{ imageSize }}%</span>
              <button class="btn-icon" @click="increaseImageSize" :disabled="imageSize >= 200">
                <i class="fas fa-search-plus"></i>
              </button>
            </div>
            <div class="view-mode-switch">
              <button
                v-for="mode in viewModes"
                :key="mode.value"
                class="btn-icon"
                :class="{ active: viewMode === mode.value }"
                @click="viewMode = mode.value"
                :title="mode.label"
              >
                <i :class="mode.icon"></i>
              </button>
            </div>
          </div>
        </div>

        <div
          class="image-grid"
          :class="viewMode"
          :style="{
            '--image-size': `${imageSize}%`,
            '--columns': viewMode === 'compact' ? 6 : 4,
          }"
        >
          <!-- 空状态提示 -->
          <div v-if="!filteredImages.length" class="empty-state">
            <i class="fas fa-image fa-3x"></i>
            <p>{{ getEmptyStateMessage() }}</p>
            <button v-if="!hasImages" class="btn btn-primary" @click="showImportDialog = true">
              <i class="fas fa-file-import"></i>
              导入图片
            </button>
          </div>
          <div
            v-for="image in currentPageImages"
            :key="image.id"
            class="image-item"
            :class="{
              selected: selectedImages.includes(image.id),
              'hover-effect': !isSelecting,
            }"
            draggable="true"
            @dragstart="handleDragStart($event, image, 'image')"
            @dragend="handleDragEnd"
            @click="handleImageClick(image)"
            @contextmenu.prevent="showContextMenu($event, image)"
          >
            <div class="image-wrapper">
              <img
                :src="image.url"
                :alt="image.name"
                :style="{ transform: `rotate(${image.rotation || 0}deg)` }"
                loading="lazy"
                @load="generateThumbnail($event, image)"
              />
              <div class="image-overlay">
                <div class="image-number" v-if="isSelecting && selectedImages.includes(image.id)">
                  {{ selectedImages.indexOf(image.id) + 1 }}
                </div>
                <div class="image-actions">
                  <button class="btn-icon" @click.stop="rotateImage(image)" title="旋转">
                    <i class="fas fa-redo"></i>
                  </button>
                  <button class="btn-icon" @click.stop="downloadImage(image)" title="下载">
                    <i class="fas fa-download"></i>
                  </button>
                  <button
                    class="btn-icon danger"
                    @click.stop="showDeleteConfirm(image)"
                    title="删除"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="image-info">
              <div class="image-meta">
                <span class="image-name">{{ image.name }}</span>
                <span class="image-size">{{ image.score }}</span>
              </div>
              <div class="image-meta">
                <span class="image-size">{{ formatSize(image.size) }}</span>
                <span class="image-group">{{ getGroupName(image.groupId) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页控制 -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            class="btn-page"
            :disabled="currentPage === 1"
            @click="handlePageChange(currentPage - 1)"
          >
            <i class="fas fa-chevron-left"></i>
          </button>

          <div class="page-numbers">
            <button
              v-for="page in totalPages"
              :key="page"
              class="btn-page"
              :class="{ active: currentPage === page }"
              @click="handlePageChange(page)"
            >
              {{ page }}
            </button>
          </div>

          <button
            class="btn-page"
            :disabled="currentPage === totalPages"
            @click="handlePageChange(currentPage + 1)"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>

        <!-- 右键菜单 -->
        <div
          v-if="contextMenu.show"
          class="context-menu"
          :style="{
            left: contextMenu.x + 'px',
            top: contextMenu.y + 'px',
          }"
        >
          <div class="menu-item" @click="handleContextMenuAction('rotate')">
            <i class="fas fa-redo"></i>
            旋转图片
          </div>
          <div class="menu-item" @click="handleContextMenuAction('moveToGroup')">
            <i class="fas fa-folder-open"></i>
            移动到分组
          </div>
          <div class="menu-item" @click="handleContextMenuAction('download')">
            <i class="fas fa-download"></i>
            下载图片
          </div>
          <div class="menu-item text-danger" @click="showDeleteConfirm(contextMenu.image)">
            <i class="fas fa-trash"></i>
            删除图片
          </div>
        </div>
      </main>
    </div>

    <!-- 导入对话框 -->
    <div v-if="showImportDialog" class="dialog-overlay" @click="showImportDialog = false">
      <div class="dialog" @click.stop>
        <h3>导入图片</h3>
        <div class="dialog-content">
          <div class="upload-info">
            <p>支持的图片格式：JPG、PNG、GIF、WebP</p>
            <p>支持文件夹导入</p>
          </div>

          <input
            type="file"
            ref="fileInput"
            multiple
            accept="image/*"
            @change="handleFileSelect"
            class="hidden"
          />

          <input
            type="file"
            ref="folderInput"
            webkitdirectory
            directory
            @change="handleFolderSelect"
            class="hidden"
          />

          <div class="import-buttons">
            <button
              class="btn btn-outline btn-block"
              @click="triggerFileInput"
              :disabled="isImporting"
            >
              <i class="fas fa-images"></i>
              选择图片
            </button>

            <button
              class="btn btn-outline btn-block"
              @click="triggerFolderInput"
              :disabled="isImporting"
            >
              <i class="fas fa-folder-open"></i>
              选择文件夹
            </button>
          </div>

          <div v-if="selectedFiles.length" class="selected-files">
            <div class="files-header">
              <h4>已选择 {{ selectedFiles.length }} 张图片</h4>
              <button class="btn-text" @click="clearSelectedFiles">清空</button>
            </div>
            <ul>
              <li v-for="file in selectedFiles" :key="file.name">
                {{ file.name }} ({{ formatSize(file.size) }})
              </li>
            </ul>
          </div>

          <div v-if="isProcessing" class="progress-bar">
            <div class="progress-inner" :style="{ width: `${processProgress}%` }">
              <span class="progress-text"> 导入中: {{ processProgress }}% </span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showImportDialog = false" :disabled="isProcessing">
            取消
          </button>
          <button
            class="btn btn-primary"
            @click="startImport"
            :disabled="!selectedFiles.length || isProcessing"
          >
            {{ isProcessing ? '导入中...' : '开始导入' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <div
      v-if="previewImage"
      class="preview-overlay"
      @click="closePreview"
      @keydown.left="showPrevImage"
      @keydown.right="showNextImage"
      @keydown.esc="closePreview"
      tabindex="0"
      ref="previewOverlay"
    >
      <div class="preview-content" @click.stop>
        <div class="preview-header">
          <h3>{{ previewImage.name }}</h3>
          <div class="preview-actions">
            <button class="btn-icon" @click="rotatePreviewImage">
              <i class="fas fa-redo"></i>
            </button>
            <button class="btn-icon" @click="downloadImage(previewImage)">
              <i class="fas fa-download"></i>
            </button>
            <button class="btn-icon" @click="closePreview">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        <div class="preview-body">
          <button class="preview-nav prev" @click="showPrevImage" :disabled="!hasPrevImage">
            <i class="fas fa-chevron-left"></i>
          </button>
          <img
            :src="previewImage.url"
            :alt="previewImage.name"
            :style="{ transform: `rotate(${previewRotation}deg)` }"
          />
          <button class="preview-nav next" @click="showNextImage" :disabled="!hasNextImage">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        <div class="preview-footer">
          <div class="image-details">
            <span>大小：{{ formatSize(previewImage.size) }}</span>
            <span>分组：{{ getGroupName(previewImage.groupId) }}</span>
          </div>
          <div class="preview-controls">
            <span>{{ currentImageIndex + 1 }} / {{ filteredImages.length }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动到分组对话框 -->
    <div
      v-if="moveToGroupDialog.show"
      class="dialog-overlay"
      @click="moveToGroupDialog.show = false"
    >
      <div class="dialog" @click.stop>
        <h3>移动到分组</h3>
        <div class="dialog-content">
          <div class="group-select">
            <div class="group-option" @click.stop="moveImageToGroup(moveToGroupDialog.image, null)">
              <i class="fas fa-folder"></i>
              <span>未分组</span>
            </div>
            <div
              v-for="group in groups"
              :key="group.id"
              class="group-option"
              @click.stop="moveImageToGroup(moveToGroupDialog.image, group.id)"
            >
              <i class="fas fa-folder"></i>
              <span>{{ group.name }}</span>
              <span class="group-count">{{ getGroupImageCount(group) }}张</span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="cancelMoveToGroup">取消</button>
        </div>
      </div>
    </div>

    <!-- 智能分组设置对话框 -->
    <div v-if="showAutoGroupDialog" class="dialog-overlay" @click="showAutoGroupDialog = false">
      <div class="dialog" @click.stop>
        <h3>智能分组设置</h3>
        <div class="dialog-content">
          <div class="form-group">
            <label>相似度阈值</label>
            <div class="slider-group">
              <input
                type="range"
                v-model="autoGroupSettings.similarityThreshold"
                min="0.5"
                max="0.9"
                step="0.05"
              />
              <span>{{ autoGroupSettings.similarityThreshold }}</span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showAutoGroupDialog = false">取消</button>
          <button class="btn btn-primary" @click="startAutoGrouping">开始分组</button>
        </div>
      </div>
    </div>

    <!-- 分组对话框 -->
    <div v-if="showGroupDialog" class="dialog-overlay" @click="showGroupDialog = false">
      <div class="dialog" @click.stop>
        <h3>{{ editingGroup ? '编辑分组' : '新建分组' }}</h3>
        <div class="dialog-content">
          <div class="form-group">
            <label>分组名称</label>
            <input
              type="text"
              v-model="groupForm.name"
              ref="groupNameInput"
              placeholder="请输入分组名称"
              @keyup.enter="handleGroupSubmit"
            />
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="groupForm.description"
              placeholder="请输入分组描述（可选）"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="groupForm.auto_sort" />
              自动排序图片
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showGroupDialog = false">取消</button>
          <button class="btn btn-primary" @click="handleGroupSubmit" :disabled="!groupForm.name">
            {{ editingGroup ? '保存' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deleteDialog.show" class="dialog-overlay" @click="cancelDelete">
      <div class="dialog" @click.stop>
        <h3>删除确认</h3>
        <div class="dialog-content">
          <p class="confirm-message">
            <i class="fas fa-exclamation-triangle text-warning"></i>
            确定要删除图片 "{{ deleteDialog.image?.name }}" 吗？
          </p>
          <p class="text-secondary">此操作无法撤销</p>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="cancelDelete" :disabled="deleteDialog.loading">取消</button>
          <button class="btn btn-danger" @click="handleDelete" :disabled="deleteDialog.loading">
            <i class="fas fa-spinner fa-spin" v-if="deleteDialog.loading"></i>
            {{ deleteDialog.loading ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 从选中创建分组对话框 -->
    <div
      v-if="createFromSelectionDialog.show"
      class="dialog-overlay"
      @click="cancelCreateFromSelection"
    >
      <div class="dialog" @click.stop>
        <h3>从选中图片创建分组</h3>
        <div class="dialog-content">
          <div class="selected-preview">
            <div class="preview-header">
              <h4>已选择 {{ selectedImages.length }} 张图片</h4>
            </div>
            <div class="preview-grid">
              <div
                v-for="imageId in selectedImages.slice(0, 6)"
                :key="imageId"
                class="preview-item"
              >
                <img
                  :src="imageStore.getImageById(imageId)?.url"
                  :alt="imageStore.getImageById(imageId)?.name"
                />
              </div>
              <div v-if="selectedImages.length > 6" class="preview-more">
                +{{ selectedImages.length - 6 }}
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>分组名称</label>
            <input
              type="text"
              v-model="createFromSelectionDialog.form.name"
              ref="createFromSelectionNameInput"
              placeholder="请输入分组名称"
              @keyup.enter="handleCreateFromSelection"
            />
          </div>

          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="createFromSelectionDialog.form.description"
              placeholder="请输入分组描述（可选）"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="createFromSelectionDialog.form.auto_sort" />
              自动排序图片
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button
            class="btn"
            @click="cancelCreateFromSelection"
            :disabled="createFromSelectionDialog.loading"
          >
            取消
          </button>
          <button
            class="btn btn-primary"
            @click="handleCreateFromSelection"
            :disabled="!createFromSelectionDialog.form.name || createFromSelectionDialog.loading"
          >
            <i class="fas fa-spinner fa-spin" v-if="createFromSelectionDialog.loading"></i>
            {{ createFromSelectionDialog.loading ? '创建中...' : '创建分组' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div v-if="toast.show" class="toast" :class="[toast.show && 'show', `toast-${toast.type}`]">
      {{ toast.message }}
    </div>

    <!-- 智能分组预览对话框 -->
    <div v-if="showGroupPreviewDialog" class="dialog-overlay" @click="cancelGroupPreview">
      <div class="dialog large" @click.stop>
        <h3>智能分组预览</h3>
        <div class="dialog-content">
          <div class="preview-stats">
            <div class="stat-item">
              <span>总分组数：</span>
              <strong>{{ groupPreview.groups.length }}</strong>
            </div>
            <div class="stat-item">
              <span>平均每组图片数：</span>
              <strong>{{ Math.round(groupPreview.averageSize) }}</strong>
            </div>
            <div class="stat-item">
              <span>未分组图片数：</span>
              <strong>{{ groupPreview.ungroupedCount }}</strong>
            </div>
          </div>

          <div class="preview-groups">
            <div v-for="group in groupPreview.groups" :key="group.id" class="preview-group">
              <div class="group-header">
                <h4>{{ group.name }}</h4>
                <span>{{ group.members.length }}张图片</span>
              </div>
              <div class="group-preview">
                <div
                  v-for="imageId in group.members.slice(0, 6)"
                  :key="imageId"
                  class="preview-item"
                >
                  <img
                    :src="imageStore.getImageById(imageId)?.url"
                    :alt="imageStore.getImageById(imageId)?.name"
                  />
                </div>
                <div v-if="group.members.length > 6" class="preview-more">
                  +{{ group.members.length - 6 }}
                </div>
              </div>
              <div class="similarity-info">
                <div
                  class="similarity-bar"
                  :style="{ width: `${group.averageSimilarity * 100}%` }"
                ></div>
                <span>平均相似度��{{ Math.round(group.averageSimilarity * 100) }}%</span>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="cancelGroupPreview">取消</button>
          <button class="btn btn-primary" @click="confirmGrouping">确认创建分组</button>
        </div>
      </div>
    </div>

    <!-- 分组预览对话框 -->
    <template v-if="showGroupPreviewDialog">
      <div class="dialog-overlay">
        <div class="dialog preview-dialog">
          <div class="dialog-header">
            <h3>分组预览</h3>
            <button class="btn-close" @click="cancelGroupPreview">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="dialog-content">
            <div class="preview-stats">
              <div class="stat-item">
                <span class="stat-label">分组数量:</span>
                <span class="stat-value">{{ groupPreview.groups.length }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均分组大小:</span>
                <span class="stat-value">{{ groupPreview.averageSize }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">未分组图片:</span>
                <span class="stat-value">{{ groupPreview.ungroupedCount }}</span>
              </div>
            </div>

            <div class="preview-groups">
              <div v-for="group in groupPreview.groups" :key="group.id" class="preview-group">
                <div class="group-header">
                  <h4>{{ group.name }}</h4>
                  <div class="group-meta">
                    <span class="similarity">
                      <i class="fas fa-percentage"></i>
                      相似度: {{ (group.similarity_score * 100).toFixed(1) }}%
                    </span>
                    <span class="face-count" v-if="group.face_count">
                      <i class="fas fa-user"></i>
                      人脸数: {{ group.face_count }}
                    </span>
                  </div>
                </div>
                <div class="group-images">
                  <div
                    v-for="imageId in group.image_ids.slice(0, 4)"
                    :key="imageId"
                    class="preview-image"
                  >
                    <img :src="getImageUrl(imageId)" :alt="getImageName(imageId)" />
                  </div>
                  <div v-if="group.image_ids.length > 4" class="more-images">
                    +{{ group.image_ids.length - 4 }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="dialog-footer">
            <button class="btn btn-secondary" @click="cancelGroupPreview">取消</button>
            <button class="btn btn-primary" @click="confirmGrouping">确认分组</button>
          </div>
        </div>
      </div>
    </template>

    <!-- 图片列表
    <div class="image-list">
      <div v-if="sortedImages.length > 0" class="image-grid">
        <div v-for="image in sortedImages" :key="image.filename" class="image-item">
          <img :src="getImageUrl(image.filename)" :alt="image.filename" @click="selectImage(image)" />
        </div>
      </div>
      <div v-else class="no-images">
        <p>暂无图片，请上传图片</p>
      </div>
    </div>-->

    <!-- 分组列表 -->
    <div class="group-list">
      <div v-if="sortedGroups.length > 0" class="group-grid">
        <div v-for="group in sortedGroups" :key="group.id" class="group-item">
          <h3>{{ group.name || '未命名分组' }}</h3>
          <div class="group-images">
            <div v-for="imageId in group.image_ids" :key="imageId" class="group-image">
              <img :src="getImageUrl(imageId)" :alt="imageId" />
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-groups">
        <p>暂无分组</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useGroupStore } from '@/stores/group'
import { useImageStore } from '@/stores/image'

import { useApiStore } from '@/stores/api'

const groupStore = useGroupStore()
const imageStore = useImageStore()
const apiStore = useApiStore()

// 本地存储键名
const STORAGE_KEY = 'image-grouping-data'

// 格式化文件大小
const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 状态管理
const searchQuery = ref('')
const groupSearchQuery = ref('')
const filterType = ref('all')
const viewMode = ref('grid')
const selectedGroup = ref(null)
const selectedImages = ref([])

const dragOverGroup = ref(null)

const showImportDialog = ref(false)
const selectedFiles = ref([])
const fileInput = ref(null)
const isSelecting = ref(false)

const maxSelectCount = ref(100)
const sortBy = ref('name')
const sortOrder = ref('asc')
const imageSize = ref(100)
const showGroupDialog = ref(false)
const editingGroup = ref(null)
const groupNameInput = ref(null)
const groupForm = ref({
  name: '',
  description: '',
  auto_sort: true,
})
const isProcessing = ref(false)
const processProgress = ref(0)
const isImporting = ref(false)
const importProgress = ref(0)
const currentPage = ref(1)
const pageSize = ref(30) // 每页显示数量

// 对话框状态
const moveToGroupDialog = ref({
  show: false,
  image: null,
})

const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  image: null,
})

// 预���相关状态
const previewImage = ref(null)
const previewRotation = ref(0)
const currentImageIndex = ref(0)
const previewOverlay = ref(null)

// 计算属性
const hasImages = computed(() => imageStore.images.length > 0)
const totalImages = computed(() => imageStore.images.length)
const groups = computed(() => groupStore.groups)
const hasPrevImage = computed(() => currentImageIndex.value > 0)
const hasNextImage = computed(() => currentImageIndex.value < filteredImages.value.length - 1)
const canSelectMore = computed(() => selectedImages.value.length < maxSelectCount.value)

// 搜索和过滤
const debouncedSearch = ref(null)
const isSearching = ref(false)

// 修改过滤后的分组计算属性
const filteredGroups = computed(() => {
  // 确保分组ID的唯一性
  const uniqueGroups = new Map()
  const allGroups = groupStore.groups

  // 如果有搜索查询，过滤分组
  if (groupSearchQuery.value) {
    const searchTerms = groupSearchQuery.value.toLowerCase().split(/\s+/)
    allGroups.forEach((group) => {
      const searchText = [
        group.name,
        group.description,
        new Date(group.createdAt).toLocaleDateString(),
        `${getGroupImageCount(group)}张图片`,
      ]
        .join(' ')
        .toLowerCase()

      if (searchTerms.every((term) => searchText.includes(term))) {
        uniqueGroups.set(group.id, group)
      }
    })
  } else {
    // 如果没有搜索，使用所有分组
    allGroups.forEach((group) => {
      uniqueGroups.set(group.id, group)
    })
  }

  // 转换回数组并排序
  return Array.from(uniqueGroups.values()).sort((a, b) => {
    const factor = groupSortOrder.value === 'asc' ? 1 : -1

    switch (groupSortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name) * factor
      case 'count':
        return (getGroupImageCount(b) - getGroupImageCount(a)) * factor
      case 'createdAt':
      default:
        return (new Date(b.createdAt) - new Date(a.createdAt)) * factor
    }
  })
})

// 过滤后的图片
const filteredImages = computed(() => {
  let images = debouncedSearch.value?.images || imageStore.images

  // 首先应用搜索过滤
  if (searchQuery.value) {
    const searchTerms = searchQuery.value.toLowerCase().split(/\s+/)
    images = images.filter((image) => {
      const searchText = [
        image.name,
        image.type,
        formatSize(image.size),
        new Date(image.createdAt).toLocaleDateString(),
        getGroupName(image.groupId),
      ]
        .join(' ')
        .toLowerCase()

      return searchTerms.every((term) => searchText.includes(term))
    })
  }

  // 根据过滤类型和选中的分组进��筛选
  if (filterType.value === 'grouped') {
    // "已分组"标签被选中时，显示所有已分组的图片
    images = images.filter((img) => img.groupId)
    // 如果同时选中了左侧具体分组，则进一步过滤
    if (selectedGroup.value) {
      images = images.filter((img) => img.groupId === selectedGroup.value.id)
    }
  } else if (filterType.value === 'ungrouped') {
    // "未分组"标签被选中时，只显示未分组的图片
    images = images.filter((img) => !img.groupId)
    // 这种情况下忽略左侧分组的选择
    // selectedGroup.value = null
  } else {
    // "全部"标签被选中时
    if (selectedGroup.value) {
      // 如果选中了具体分组，只显示该分组的图片
      images = images.filter((img) => img.groupId === selectedGroup.value.id)
    }
  }
  // 排序
  return images.sort((a, b) => {
    const factor = sortOrder.value === 'asc' ? 1 : -1

    if (sortBy.value === 'name') {
      return a.name.localeCompare(b.name) * factor
    } else if (sortBy.value === 'size') {
      return (a.size - b.size) * factor
    } else if (sortBy.value === 'createdAt') {
      return (new Date(a.createdAt) - new Date(b.createdAt)) * factor
    } else if (sortBy.value === 'group') {
      // 按分组排序
      const groupA = getGroupName(a.groupId)
      const groupB = getGroupName(b.groupId)

      // 首先按分组名称排序
      const groupCompare = groupA.localeCompare(groupB)
      if (groupCompare !== 0) {
        return groupCompare * factor
      }

      // 如果分组相同，则按名称排序
      return a.name.localeCompare(b.name) * factor
    }

    return 0
  })
})

// 未分组图片数量
const ungroupedCount = computed(() => imageStore.images.filter((img) => !img.groupId).length)

// 视图模式选项
const viewModes = [
  { value: 'grid', label: '网格视图', icon: 'fas fa-th' },
  { value: 'list', label: '列表视图', icon: 'fas fa-list' },
  { value: 'compact', label: '紧凑视图', icon: 'fas fa-th-large' },
]

// 过滤类型选项
const filterTypes = [
  { value: 'all', label: '全部' },
  { value: 'grouped', label: '已分组' },
  { value: 'ungrouped', label: '未分组' },
]

// 分组操作方法
const selectGroup = (group) => {
  // 如果当前是"未分组"过滤状态，切换到"全部"
  if (filterType.value === 'ungrouped') {
    filterType.value = 'all'
  }
  selectedGroup.value = group
  selectedImages.value = []
}

const getGroupName = (groupId) => {
  if (!groupId) return '未分组'
  const group = groupStore.getGroupById(groupId)
  return group ? group.name : '未知分组'
}

const getGroupImageCount = (group) => {
  return imageStore.getImagesByGroupId(group.id).length
}

const createGroup = () => {
  editingGroup.value = null
  groupForm.value = {
    name: '',
    description: '',
    auto_sort: true,
  }
  showGroupDialog.value = true
  nextTick(() => {
    groupNameInput.value?.focus()
  })
}

const editGroup = (group) => {
  editingGroup.value = group
  groupForm.value = {
    name: group.name,
    description: group.description,
    auto_sort: group.auto_sort ?? true,
  }
  showGroupDialog.value = true
  nextTick(() => {
    groupNameInput.value?.focus()
  })
}

const handleGroupSubmit = async () => {
  try {
    if (!groupForm.value.name) return

    const group = {
      id: editingGroup.value?.id || Date.now().toString(),
      name: groupForm.value.name,
      description: groupForm.value.description,
      auto_sort: groupForm.value.auto_sort,
      created_at: editingGroup.value?.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    if (editingGroup.value) {
      await apiStore.updateGroup(group.id, group)
      await groupStore.updateGroup(group)
    } else {
      const createdGroup = await apiStore.createGroup(group)
      await groupStore.createGroup(createdGroup)

      if (selectedImages.value.length) {
        await imageStore.moveImagesToGroup(selectedImages.value, createdGroup.id)
        selectedImages.value = []
      }
    }

    showGroupDialog.value = false
    showToast(`分组${editingGroup.value ? '更新' : '创建'}成功`)
  } catch (error) {
    console.error('保存分组失败:', error)
    showToast('保存分组失败：' + error.message, 'error')
  }
}

const createGroupFromSelection = () => {
  showCreateFromSelectionDialog()
}

const deleteGroup = async (groupId) => {
  if (!confirm('确定要删除该分组吗？删除后组内图片将变为未分组状态。')) return

  try {
    // 调用后端 API 删除分组
    await apiStore.deleteGroup(groupId)

    // 更新本地状态
    const groupImages = imageStore.getImagesByGroupId(groupId)
    for (const image of groupImages) {
      await imageStore.updateImage(image.id, {
        groupId: null,
        updatedAt: new Date().toISOString(),
      })
    }

    await groupStore.deleteGroup(groupId)

    if (selectedGroup.value?.id === groupId) {
      selectedGroup.value = null
    }

    showToast(`分组删除成功，${groupImages.length} 张图片已移至未分组`)
  } catch (error) {
    console.error('删除分组失败:', error)
    showToast('删除分组失败：' + error.message, 'error')
  }
}

// 图片操作方法
const rotateImage = (image) => {
  image.rotation = ((image.rotation || 0) + 90) % 360
  imageStore.updateImage(image)
}

const downloadImage = (image) => {
  const link = document.createElement('a')
  link.href = image.url
  link.download = image.name
  link.click()
}

// 批量操作法
const toggleSelectionMode = () => {
  isSelecting.value = !isSelecting.value
  if (!isSelecting.value) {
    selectedImages.value = []
  }
}

const handleImageClick = (image) => {
  if (isSelecting.value) {
    const index = selectedImages.value.indexOf(image.id)
    if (index === -1) {
      if (canSelectMore.value) {
        selectedImages.value.push(image.id)
      } else {
        showToast(`最多只能选择 ${maxSelectCount.value} 张图片`)
      }
    } else {
      // 修复预览逻辑
      previewImage.value = image
      currentImageIndex.value = filteredImages.value.findIndex((img) => img.id === image.id)
      previewRotation.value = image.rotation || 0
    }
  }
}

// 导入相关方法
const MAX_FILE_SIZE = 1024 * 1024 * 1024 // 1GB

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event) => {
  const files = Array.from(event.target.files)
  if (!files.length) return

  try {
    isImporting.value = true
    await imageStore.importImages(files)
    showImportDialog.value = false
    showToast('导入成功')
  } catch (error) {
    console.error('导入失败:', error)
    showToast('导入失败：' + error.message, 'error')
  } finally {
    isImporting.value = false
    // 清空文件输入
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const startImport = async () => {
  if (!selectedFiles.value.length) return

  try {
    isImporting.value = true
    importProgress.value = 0

    // Import all files at once using importImages
    const newImages = await importImages(selectedFiles.value)

    // Update progress
    importProgress.value = 100

    // Show success message and close dialog
    showToast(`成功导入 ${newImages.length} 张图片`)
    showImportDialog.value = false
    selectedFiles.value = []

    // Clear file inputs
    if (fileInput.value) fileInput.value.value = ''
    if (folderInput.value) folderInput.value.value = ''
  } catch (error) {
    console.error('导入失败:', error)
    showToast('导入失败：' + (error instanceof Error ? error.message : String(error)), 'error')
  } finally {
    isImporting.value = false
    importProgress.value = 0
  }
}

const clearSelectedFiles = () => {
  selectedFiles.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 从本地存储加载数据
const loadFromStorage = () => {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    if (data) {
      const { images, groups } = JSON.parse(data)
      if (images?.length) {
        imageStore.setImages(images)
      }
      if (groups?.length) {
        groupStore.setGroups(groups)
      }
    }
  } catch (error) {
    console.error('加载本地数据失败:', error)
  }
}

// 监听数据变化，保存到本地存储
watch(
  () => imageStore.images,
  (newImages) => {
    const currentData = JSON.parse(
      localStorage.getItem(STORAGE_KEY) || '{"images": [], "groups": []}',
    )
    currentData.images = newImages
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentData))
  },
  { deep: true },
)

watch(
  () => groupStore.groups,
  (newGroups) => {
    const currentData = JSON.parse(
      localStorage.getItem(STORAGE_KEY) || '{"images": [], "groups": []}',
    )
    currentData.groups = newGroups
    localStorage.setItem(STORAGE_KEY, JSON.stringify(currentData))
  },
  { deep: true },
)

// 监听
watch(isSelecting, (newValue) => {
  if (!newValue) {
    selectedImages.value = []
  }
})

watch(
  () => imageStore.images,
  () => {
    if (previewImage.value) {
      const image = imageStore.getImageById(previewImage.value.id)
      if (!image) {
        closePreview()
      }
    }
  },
  { deep: true },
)

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', closeContextMenu)

  // 加载用户偏好设置
  const savedViewMode = localStorage.getItem('preferredViewMode')
  if (savedViewMode) {
    viewMode.value = savedViewMode
  }

  const savedImageSize = localStorage.getItem('preferredImageSize')
  if (savedImageSize) {
    imageSize.value = parseInt(savedImageSize)
  }

  loadFromStorage()

  // 添加键盘事件监听
  document.addEventListener('keydown', (e) => {
    if (previewImage.value) {
      if (e.key === 'Escape') {
        closePreview()
      } else if (e.key === 'ArrowLeft') {
        showPrevImage()
      } else if (e.key === 'ArrowRight') {
        showNextImage()
      }
    }
  })
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)

  // 移除键盘事件监听
  document.removeEventListener('keydown', (e) => {
    if (previewImage.value) {
      if (e.key === 'Escape') {
        closePreview()
      } else if (e.key === 'ArrowLeft') {
        showPrevImage()
      } else if (e.key === 'ArrowRight') {
        showNextImage()
      }
    }
  })
})

// 排相关法
const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

// 图片控制
const increaseImageSize = () => {
  if (imageSize.value < 200) {
    imageSize.value += 20
    localStorage.setItem('preferredImageSize', imageSize.value.toString())
  }
}

const decreaseImageSize = () => {
  if (imageSize.value > 100) {
    imageSize.value -= 20
    localStorage.setItem('preferredImageSize', imageSize.value.toString())
  }
}

const moveImageToGroup = async (image, groupId) => {
  try {
    await imageStore.updateImage(image.id, {
      groupId: groupId,
    })

    moveToGroupDialog.value.show = false
    showToast('移动成功')
  } catch (error) {
    console.error('移动失败:', error)
    showToast('移动失败：' + error.message, 'error')
  }
}

const cancelMoveToGroup = () => {
  moveToGroupDialog.value.show = false
}

// 辅助方法
const getEmptyStateMessage = () => {
  if (!hasImages.value) {
    return '还没有任何图片，快来导入一些图片吧！'
  }
  if (searchQuery.value) {
    return '没找到匹配图'
  }
  if (selectedGroup.value === null) {
    return '没有未分组的片'
  }
  return '该分组下没有图片'
}

// 右键菜单相关方法
const showContextMenu = (event, image) => {
  event.preventDefault()
  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    image: image,
  }
}

const closeContextMenu = () => {
  contextMenu.value.show = false
}

// 在点其他地方时关闭右键菜单
onMounted(() => {
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})

const handleContextMenuAction = async (action) => {
  const image = contextMenu.value.image
  if (!image) return

  try {
    switch (action) {
      case 'rotate':
        rotateImage(image)
        break
      case 'download':
        downloadImage(image)
        break
      case 'delete':
        if (confirm('确定要删除这张图片吗？')) {
          await imageStore.deleteImage(image.id)
          showToast('删除成功')
        }
        break
      case 'moveToGroup':
        moveToGroupDialog.value = {
          show: true,
          image: image,
        }
        break
    }
  } catch (error) {
    console.error('操作失败:', error)
    showToast('操作失败：' + error.message, 'error')
  } finally {
    contextMenu.value.show = false
  }
}

// 智能分组相关状态
const autoGroupSettings = ref({
  similarityThreshold: 0.7, // 相似度阈值
  minGroupSize: 2, // 最小分组大小
  maxGroupSize: 20, // 最大分组大小
  considerExif: true, // 考虑EXIF信息
  groupByDate: true, // 按日期分组
  dateThreshold: 3600 * 1000, // 时间阈值（1小时内）
  colorWeight: 0.5, // 颜色特征权重
  dateWeight: 0.2, // 时间特征权重
  sizeWeight: 0.1, // 尺寸特征权重
  compositionWeight: 0.2, // 构图特征权重
  useAdvancedFeatures: true, // 使用高级特征
  previewBeforeCreate: true, // 创建前预览
  groupingStrategy: 'balanced', // 分组策略：balanced(平衡) / strict(严格) / loose(宽松)
})

const showAutoGroupDialog = ref(false)
const groupingStatus = ref({
  currentStep: '',
  totalSteps: 0,
  currentProgress: 0,
  processedImages: 0,
  totalImages: 0,
})

// 智能分组方法
const showAutoGroupSettings = () => {
  showAutoGroupDialog.value = true
}

// 添加预览相关状态
const showGroupPreviewDialog = ref(false)
const groupPreview = ref({
  groups: [],
  averageSize: 0,
  ungroupedCount: 0,
})

const cancelGroupPreview = () => {
  showGroupPreviewDialog.value = false
  groupPreview.value = {
    groups: [],
    averageSize: 0,
    ungroupedCount: 0,
  }
}

const confirmGrouping = async () => {
  try {
    await createGroupsFromClusters(groupPreview.value.groups)
    showToast('智能分组创建成功')
  } catch (error) {
    console.error('创建分组失败:', error)
    showToast('创建分组失败：' + error.message, 'error')
  } finally {
    showGroupPreviewDialog.value = false
  }
}

// 修改智能分组流程
const startAutoGrouping = async () => {
  if (!hasImages.value || isProcessing.value) return

  try {
    isProcessing.value = true
    groupingStatus.value = {
      currentStep: '准备分析图片',
      totalSteps: 3,
      currentProgress: 0,
      processedImages: 0,
      totalImages: imageStore.images.length,
    }

    // 获取所有未分组的图片ID
    const ungroupedImageIds = imageStore.images.filter((img) => !img.groupId).map((img) => img.id)

    if (ungroupedImageIds.length === 0) {
      showToast('没有可分组的图片', 'warning')
      return
    }

    // 调用后端 API 进行智能分组
    const { data: groupResults } = await apiStore.groupImages(
      ungroupedImageIds,
      autoGroupSettings.value.similarityThreshold,
    )
    // 创建分组并移动图片
    for (const result of groupResults) {
      // 创建新分组
      const group = {
        id: result.group_id,
        name: result.name,
        description: `相似度: ${Math.round(result.similarity_score * 100)}%`,
        auto_sort: true,
        created_at: new Date().toISOString(),
      }

      // 保存分组
      await groupStore.createGroup(group)

      // 移动图片到分组
      await imageStore.moveImagesToGroup(result.image_ids, group.id)

      groupingStatus.value.processedImages += result.image_ids.length
      groupingStatus.value.currentProgress =
        (groupingStatus.value.processedImages / groupingStatus.value.totalImages) * 100
    }

    showToast('智能分组完成')
  } catch (error) {
    console.error('智能分组失败:', error)
    showToast('智能分组失败：' + error.message, 'error')
  } finally {
    isProcessing.value = false
    showAutoGroupDialog.value = false
  }
}

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(filteredImages.value.length / pageSize.value)
})

// 当前页的图片
const currentPageImages = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredImages.value.slice(start, end)
})

// 分页方法
const handlePageChange = (page) => {
  currentPage.value = page
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 状态管理
const deleteDialog = ref({
  show: false,
  image: null,
  loading: false,
})

// 删除相关方法
const showDeleteConfirm = (image) => {
  deleteDialog.value = {
    show: true,
    image: image,
    loading: false,
  }
  // 关闭右键菜单
  contextMenu.value.show = false
}

const handleDelete = async () => {
  try {
    deleteDialog.value.loading = true

    // 调用后端 API 删除图片
    await apiStore.deleteImage(deleteDialog.value.image.id)

    // 从本地状态中删除图片
    await imageStore.deleteImage(deleteDialog.value.image.id)

    showToast('删除成功')
    deleteDialog.value.show = false
  } catch (error) {
    console.error('删除失败:', error)
    showToast('删除失败：' + error.message, 'error')
  } finally {
    deleteDialog.value.loading = false
  }
}

const cancelDelete = () => {
  deleteDialog.value.show = false
}

// 从选中创建分组对话框状态
const createFromSelectionDialog = ref({
  show: false,
  loading: false,
  form: {
    name: '',
    description: '',
    auto_sort: true,
  },
})

const createFromSelectionNameInput = ref(null)

// 从选中创建分组相关方法
const showCreateFromSelectionDialog = () => {
  if (!selectedImages.value.length) {
    showToast('先选择要添加到分组的图片', 'warning')
    return
  }

  createFromSelectionDialog.value = {
    show: true,
    loading: false,
    form: {
      name: '',
      description: `包含 ${selectedImages.value.length} 张图片`,
      auto_sort: true,
    },
  }

  nextTick(() => {
    createFromSelectionNameInput.value?.focus()
  })
}

const handleCreateFromSelection = async () => {
  if (!createFromSelectionDialog.value.form.name) return

  try {
    createFromSelectionDialog.value.loading = true

    // 1. 创建分组
    const group = {
      id: Date.now().toString(),
      name: createFromSelectionDialog.value.form.name,
      description: createFromSelectionDialog.value.form.description,
      auto_sort: createFromSelectionDialog.value.form.auto_sort,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    // 2. 保存选中的图片ID，因为后面会清空选择
    const selectedImageIds = [...selectedImages.value]

    // 3. 创建分组并待完成
    await groupStore.createGroup(group)

    // 4. 移动图片到新分组
    await imageStore.moveImagesToGroup(selectedImageIds, group.id)

    // 5. 清空选择并关闭对话框
    selectedImages.value = []
    createFromSelectionDialog.value.show = false

    // 6. 示成功提示
    showToast(`成功创建分组 "${group.name}" 并移动了 ${selectedImageIds.length} 张图片`)
  } catch (error) {
    console.error('创建分组失败:', error)
    showToast('创建分组失败：' + error.message, 'error')
  } finally {
    createFromSelectionDialog.value.loading = false
  }
}

const cancelCreateFromSelection = () => {
  createFromSelectionDialog.value.show = false
}

// 预览相关方法
const closePreview = () => {
  previewImage.value = null
  previewRotation.value = 0
  currentImageIndex.value = 0
}

const rotatePreviewImage = () => {
  previewRotation.value = (previewRotation.value + 90) % 360
}

const showPrevImage = () => {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
    previewImage.value = filteredImages.value[currentImageIndex.value]
    previewRotation.value = previewImage.value.rotation || 0
  }
}

const showNextImage = () => {
  if (currentImageIndex.value < filteredImages.value.length - 1) {
    currentImageIndex.value++
    previewImage.value = filteredImages.value[currentImageIndex.value]
    previewRotation.value = previewImage.value.rotation || 0
  }
}

// Toast 相关状态
const toast = ref({
  show: false,
  message: '',
  type: 'info', // 'info', 'success', 'error', 'warning'
  timer: null,
})

// Toast 工具方法
const showToast = (message, type = 'success') => {
  if (toast.value.timer) {
    clearTimeout(toast.value.timer)
  }

  toast.value = {
    show: true,
    message,
    type,
    timer: setTimeout(() => {
      toast.value.show = false
    }, 3000),
  }
}

// 批量选择相关方法
const selectAll = () => {
  selectedImages.value = filteredImages.value.map((img) => img.id)
}

const deselectAll = () => {
  selectedImages.value = []
}

const invertSelection = () => {
  const currentSelection = new Set(selectedImages.value)
  selectedImages.value = filteredImages.value
    .filter((img) => !currentSelection.has(img.id))
    .map((img) => img.id)
}

// 拖拽相关状态
const draggedImage = ref(null)

// 拖拽相关方法
const handleDragStart = (event, image) => {
  draggedImage.value = image
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', image.id)

  // 添加拖动的视觉效果
  event.target.closest('.image-item').classList.add('dragging')
}

const handleDragEnd = () => {
  draggedImage.value = null
  dragOverGroup.value = null

  // 除拖动时的视觉效果
  const draggedElement = document.querySelector('.image-item.dragging')
  if (draggedElement) {
    draggedElement.classList.remove('dragging')
  }
}

const handleDragOver = (event, group) => {
  if (!draggedImage.value) return

  event.preventDefault()
  dragOverGroup.value = group.id
  event.dataTransfer.dropEffect = 'move'
}

const handleDragLeave = (group) => {
  if (dragOverGroup.value === group.id) {
    dragOverGroup.value = null
  }
}

const handleDrop = async (event, group) => {
  if (!draggedImage.value) return

  try {
    // 移动图片到目标分组
    await imageStore.moveImagesToGroup([draggedImage.value.id], group.id)

    showToast(`已将图片 "${draggedImage.value.name}" 移动到组 "${group.name}"`)
  } catch (error) {
    console.error('移动图片失败:', error)
    showToast('移动图片失败：' + error.message, 'error')
  } finally {
    draggedImage.value = null
    dragOverGroup.value = null
  }
}

// 图片优化相关方法
const generateThumbnail = async (event, image) => {
  try {
    const img = event.target
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    // 设置缩略图最大尺寸
    const maxSize = 400
    let width = img.naturalWidth
    let height = img.naturalHeight

    // 计算缩放比例
    if (width > height) {
      if (width > maxSize) {
        height = Math.round((height * maxSize) / width)
        width = maxSize
      }
    } else {
      if (height > maxSize) {
        width = Math.round((width * maxSize) / height)
        height = maxSize
      }
    }

    // 设置画布尺寸
    canvas.width = width
    canvas.height = height

    // 绘制图片
    ctx.fillStyle = '#f1f2f6' // 背景色
    ctx.fillRect(0, 0, width, height)
    ctx.drawImage(img, 0, 0, width, height)

    // 转换为 WebP 格式（如果浏览器支持）
    const thumbnailUrl = canvas.toDataURL('image/webp', 0.8)

    // 更新图片数据
    await imageStore.updateImage(image.id, {
      thumbnailUrl,
      width,
      height,
      aspectRatio: width / height,
      updatedAt: new Date().toISOString(),
    })

    // 添加加载完成的类名
    img.classList.add('loaded')
  } catch (error) {
    console.error('生成缩略图失败:', error)
  }
}

// 修改过滤类型切换的监听
watch(filterType, (newType) => {
  // 当切换到"未分组"时，清除选中的分组
  if (newType === 'ungrouped') {
    selectedGroup.value = null
  }
})

// 在状态管理部分添加分组排序相关的状态
const groupSortBy = ref('createdAt')
const groupSortOrder = ref('desc')

// 添加分组排序方法
const toggleGroupSortOrder = () => {
  groupSortOrder.value = groupSortOrder.value === 'asc' ? 'desc' : 'asc'
}

// 添加创建分组的函
const createGroupsFromClusters = async (clusters) => {
  try {
    // 创建分组并移动图片
    for (const cluster of clusters) {
      // 创建新分组
      const group = {
        id: cluster.id,
        name: `智能分组 ${clusters.indexOf(cluster) + 1}`,
        description: `包含 ${cluster.members.length} 张相似图片`,
        auto_sort: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }

      // 保存分组
      await groupStore.createGroup(group)

      // 移动图片到分组
      await imageStore.moveImagesToGroup(cluster.members, group.id)
    }

    // 清理空分组
    const emptyGroups = groupStore.groups.filter(
      (group) => imageStore.getImagesByGroupId(group.id).length === 0,
    )

    for (const group of emptyGroups) {
      await groupStore.deleteGroup(group.id)
    }
  } catch (error) {
    console.error('创分组失败:', error)
    throw error
  }
}

// 修改图片导入函数
const importImages = async (files) => {
  try {
    isImporting.value = true
    const { data: imageIds } = await apiStore.uploadImages(files)
    // 将返回的图片ID添加到 imageStore
    const newImages = await Promise.all(
      imageIds.map(async (id) => {
        const imageData = await apiStore.getImage(id)
        return imageData
      }),
    )
    await imageStore.setImages([...imageStore.images, ...newImages])
    return newImages
  } catch (error) {
    console.error('导入图片失败:', error)
    throw error
  } finally {
    isImporting.value = false
  }
}

const folderInput = ref(null)

// 触发文件夹选择
const triggerFolderInput = () => {
  // 直接调用新的文件夹选择方法
  handleFolderSelect()
}

// 处理文件夹选择
const handleFolderSelect = async () => {
  try {
    // 检查 showDirectoryPicker API 是否可用
    if (!('showDirectoryPicker' in window)) {
      showToast('您的浏览器不支持文件夹选择功能，请使用最新版本的 Chrome 或 Edge 浏览器', 'error')
      return
    }

    const handle = await window.showDirectoryPicker().catch((error) => {
      if (error.name === 'AbortError') {
        // 用户取消了选择
        return null
      }
      throw error
    })

    if (!handle) return

    // 验证权限
    const permissionStatus = await handle.queryPermission({ mode: 'read' })
    if (permissionStatus !== 'granted') {
      const requestPermission = await handle.requestPermission({ mode: 'read' })
      if (requestPermission !== 'granted') {
        showToast('需要文件夹访问权限才能导入图片', 'error')
        return
      }
    }

    // 递归获取所有图片文件
    const imageFiles = []

    async function* getFilesRecursively(dirHandle) {
      for await (const entry of dirHandle.values()) {
        if (entry.kind === 'directory') {
          yield* getFilesRecursively(entry)
        } else if (entry.kind === 'file') {
          const file = await entry.getFile()
          if (file.type.startsWith('image/') && file.size <= MAX_FILE_SIZE) {
            imageFiles.push(file)
          }
        }
      }
    }

    isProcessing.value = true
    try {
      for await (const a of getFilesRecursively(handle)) {
        // 这里不需要做任何事，因为文件已经被添加到 imageFiles 数组中
        console.log(a)
      }

      if (!imageFiles.length) {
        showToast('所选文件夹中没有有效的图片文件', 'warning')
        return
      }

      selectedFiles.value = imageFiles
      showToast(`找到 ${imageFiles.length} 张图片`)
    } finally {
      isProcessing.value = false
    }
  } catch (error) {
    console.error('选择文件夹失败:', error)
    if (error.name === 'SecurityError') {
      showToast('没有权限访问文件系统，请检查浏览器设置', 'error')
    } else {
      showToast('选择文件夹失败：' + error.message, 'error')
    }
  }
}

// 计算属性：排序后的分组
const sortedGroups = computed(() => {
  if (!groups.value) return []
  return [...groups.value].sort((a, b) => {
    // 确保 name 属性存在，如果不存在则使用空字符串
    const nameA = a?.name || ''
    const nameB = b?.name || ''
    return nameA.localeCompare(nameB)
  })
})
</script>

<style scoped>
.grouping-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--background-color);
}

.page-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.group-sidebar {
  width: 280px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.group-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.group-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.group-item {
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: background-color 0.2s;
}

.group-item:hover {
  background: var(--background-hover);
}

.group-item.active {
  background: var(--primary-color);
  color: white;
}

.image-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.image-grid {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-auto-rows: min-content; /* 让每行高度自适应内容 */
}

.image-item {
  position: relative;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: auto; /* 高度自适应内容 */
}

.image-item:hover {
  transform: translateY(-2px) translateZ(0);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.image-item.selected {
  outline: 3px solid var(--primary-color);
  outline-offset: -3px;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加速 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-item:hover .image-overlay,
.image-item.selected .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-number {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  background: var(--primary-color);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: bold;
  z-index: 2;
}

.image-info {
  padding: 0.75rem;
  background: white;
  border-top: 1px solid var(--background-color);
  flex-shrink: 0; /* 防止信息区域被压缩 */
}

.image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 新增和修改的样式 */
.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0;
}

.progress-bar {
  height: 4px;
  background: var(--background-color);
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.group-toolbar {
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.search-bar {
  position: relative;
  flex: 1;
}

.search-bar input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
  font-size: 0.875rem;
}

.search-bar i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.group-item .group-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.group-item .group-actions {
  display: none;
  gap: 0.25rem;
}

.group-item:hover .group-actions {
  display: flex;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-right: 1rem;
}

.filter-controls select {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
  color: var(--text-primary);
  outline: none;
}

.image-item.selected {
  outline: 2px solid var(--primary-color);
}

.selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.dialog-content {
  padding: 1rem;
}

.dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.dialog-content .form-group {
  margin-bottom: 1rem;
}

.dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.dialog-content .form-group input[type='text'],
.dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-wrapper img.loaded {
  opacity: 1;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: rgb(5, 5, 5);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.btn-icon.danger:hover {
  background: var(--error-color);
}

.image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-size {
  opacity: 0.8;
}

.image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.context-menu .menu-item:hover {
  background: var(--background-color);
}

.context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.filter-group {
  display: flex;
  gap: 0.25rem;
}

.btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.btn-text:hover {
  background: var(--background-hover);
}

.btn-text.active {
  background: var(--primary-color);
  color: white;
}

/* 预览弹窗样式 */
.preview-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
  outline: none;
}

.preview-content {
  max-width: 90vw;
  max-height: 90vh;
  background: white;
  border-radius: var(--border-radius);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.preview-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.preview-body {
  flex: 1;
  overflow: hidden;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  background: var(--background-color);
  position: relative;
}

.preview-body img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.preview-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  padding: 1rem;
  cursor: pointer;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.preview-nav:hover {
  background: rgba(255, 255, 255, 0.2);
}

.preview-nav:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.preview-nav.prev {
  left: 1rem;
}

.preview-nav.next {
  right: 1rem;
}

.preview-footer {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color);
  background: var(--background-color);
}

.image-details {
  display: flex;
  gap: 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.preview-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* 分组选择对话框 */
.group-select {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.group-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.group-option:hover {
  background: var(--background-color);
}

.group-option i {
  color: var(--primary-color);
}

.group-option .group-count {
  margin-left: auto;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 导入对话框样式 */
.upload-info {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--background-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.upload-info p {
  margin: 0.25rem 0;
}

.selected-files {
  margin-top: 1rem;
  max-height: 200px;
  overflow-y: auto;
}

.selected-files ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  font-size: 0.875rem;
}

.selected-files li {
  margin: 0.25rem 0;
  color: var(--text-secondary);
}

.hidden {
  display: none;
}

.btn-block {
  display: block;
  width: 100%;
  text-align: center;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.files-header h4 {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.upload-info {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--background-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  color: var(--text-secondary);
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

/* 右键菜单样式 */
.context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.context-menu .menu-item:hover {
  background: var(--background-color);
}

.context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 2rem;
  padding: 1rem;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.btn-page {
  width: 36px;
  height: 36px;
  border: none;
  background: white;
  border-radius: var(--border-radius);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled) {
  background: var(--background-color);
  color: var(--primary-color);
}

.btn-page.active {
  background: var(--primary-color);
  color: white;
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm-message {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.text-warning {
  color: var(--warning-color);
}

.text-secondary {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.btn-danger {
  background: var(--error-color);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: var(--error-hover-color);
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 0.5rem;
  margin: 1rem 0;
}

.preview-item {
  position: relative;
  padding-top: 100%;
  background: var(--background-color);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.preview-item img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-more {
  position: relative;
  padding-top: 100%;
  background: var(--background-color);
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--text-secondary);
}

.preview-more::before {
  content: attr(data-count);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.selected-preview {
  background: var(--background-color);
  border-radius: var(--border-radius);
  padding: 1rem;
  margin-bottom: 1rem;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.preview-header h4 {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.selection-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1rem;
  border-right: 1px solid var(--border-color);
}

.selection-info {
  padding: 0.25rem 0.5rem;
  background: var(--background-color);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.btn-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: none;
  background: none;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: all 0.2s;
}

.btn-text:hover:not(:disabled) {
  background: var(--background-hover);
}

.btn-text:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-text i {
  font-size: 0.875rem;
}

.group-item.drag-over {
  background: var(--primary-light);
  border: 2px dashed var(--primary-color);
}

.image-item.dragging {
  opacity: 0.5;
  transform: scale(0.95);
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.sort-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 0.875rem;
  outline: none;
}

.sort-select:hover {
  border-color: var(--primary-color);
}

.slider-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider-group input[type='range'] {
  flex: 1;
}

.size-inputs {
  display: flex;
  gap: 1rem;
}

.size-inputs > div {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.weight-sliders {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.weight-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.weight-item input[type='range'] {
  flex: 1;
}

.time-threshold {
  margin-top: 0.5rem;
  margin-left: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.time-threshold input {
  width: 80px;
}

/* 预览对话框样式 */
.dialog.large {
  max-width: 900px;
  width: 90%;
}

.preview-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: var(--border-radius);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-groups {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  max-height: 60vh;
  overflow-y: auto;
  padding: 0.5rem;
}

.preview-group {
  background: var(--background-color);
  border-radius: var(--border-radius);
  padding: 1rem;
}

.group-preview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.similarity-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.similarity-bar {
  height: 4px;
  background: var(--primary-color);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.similarity-info span {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 修改网格视图模式 */
.image-grid.grid {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

/* 修改列表视图模式 */
.image-grid.list {
  grid-template-columns: 1fr;
}

.image-grid.list .image-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  height: auto;
}

.image-grid.list .image-wrapper {
  width: 120px;
  min-width: 120px;
  padding-bottom: 90px; /* 4:3 的宽高比 */
  margin-right: 1rem;
}

.image-grid.list .image-info {
  flex: 1;
  border-top: none;
}

/* 修改紧凑视图模式 */
.image-grid.compact {
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.5rem;
}

.image-grid.compact .image-wrapper {
  padding-bottom: 75%; /* 保持 4:3 的宽高比 */
}

.image-grid.compact .image-info {
  padding: 0.5rem;
}

.image-grid.compact .image-name {
  font-size: 0.875rem;
}

.image-grid.compact .image-meta {
  font-size: 0.75rem;
}

.import-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.import-buttons .btn {
  flex: 1;
}

.group-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9em;
  color: #666;
}

.similarity,
.face-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.similarity i,
.face-count i {
  font-size: 0.8em;
}

/* 图片列表 */
.image-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.image-list .image-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-auto-rows: min-content; /* 让每行高度自适应内容 */
}

.image-list .image-item {
  position: relative;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: auto; /* 高度自适应内容 */
}

.image-list .image-item:hover {
  transform: translateY(-2px) translateZ(0);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.image-list .image-item.selected {
  outline: 3px solid var(--primary-color);
  outline-offset: -3px;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加速 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay,
.image-list .image-item.selected .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-number {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  background: var(--primary-color);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: bold;
  z-index: 2;
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-top: 1px solid var(--background-color);
  flex-shrink: 0; /* 防止信息区域被压缩 */
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 的宽高比 */
  overflow: hidden;
  background: var(--background-color);
}

.image-list .image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain; /* 改为 contain 以显示完整图片 */
  background: var(--background-color);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-list .image-wrapper img.loaded {
  opacity: 1;
}

.image-list .image-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 0.75rem;
  opacity: 0;
  transform: translateZ(0); /* 启用GPU加 */
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity;
}

.image-list .image-item:hover .image-overlay {
  opacity: 1;
  pointer-events: auto;
}

.image-list .image-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  transform: translateZ(0); /* 启用GPU加速 */
}

.image-list .btn-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateZ(0); /* 启用GPU加速 */
  transition: background-color 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: background-color;
}

.image-list .btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.image-list .btn-icon.danger:hover {
  background: var(--error-color);
}

.image-list .image-info {
  padding: 0.75rem;
  background: white;
  border-radius: 0 0 var(--border-radius) var(--border-radius);
}

.image-list .image-name {
  display: block;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-list .image-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.image-list .image-size {
  opacity: 0.8;
}

.image-list .image-group {
  color: var(--primary-color);
}

/* 右键菜单 */
.image-list .context-menu {
  position: fixed;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 0.5rem;
  min-width: 160px;
  z-index: 1000;
}

.image-list .context-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.image-list .context-menu .menu-item:hover {
  background: var(--background-color);
}

.image-list .context-menu .menu-item i {
  width: 16px;
  opacity: 0.8;
}

.image-list .context-menu .text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}

/* 尺寸控制 */
.image-list .size-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 1rem;
  padding: 0 1rem;
  border-left: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
}

.image-list .size-value {
  min-width: 3em;
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* 过滤器组 */
.image-list .filter-group {
  display: flex;
  gap: 0.25rem;
}

.image-list .btn-text {
  padding: 0.25rem 0.5rem;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
}

.image-list .btn-text:hover {
  background: var(--background-hover);
}

.image-list .btn-text.active {
  background: var(--primary-color);
  color: white;
}

.image-list .image-item.selected {
  outline: 2px solid var(--primary-color);
}

.image-list .selection-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.image-list .empty-state {
  grid-column: 1 / -1;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary);
}

.image-list .empty-state i {
  margin-bottom: 1rem;
  opacity: 0.5;
}

.image-list .dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-list .dialog {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.image-list .dialog h3 {
  margin: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.image-list .dialog-content {
  padding: 1rem;
}

.image-list .dialog-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.image-list .dialog-content .form-group {
  margin-bottom: 1rem;
}

.image-list .dialog-content .form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
}

.image-list .dialog-content .form-group input[type='text'],
.image-list .dialog-content .form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.image-list .image-wrapper {
  position: relative;

  background: var(--background-color);
}

.image-list .dialog-content .form-group textarea {
  resize: vertical;
  min-height: 80px;
}
</style>
