<template>
  <div class="app">
    <nav class="sidebar">
      <div class="sidebar-content">
        <div class="nav-brand">
          <router-link to="/" class="brand">
            <div class="brand-icon">
              <i class="fas fa-layer-group"></i>
            </div>
            <span class="brand-text">AI Vision</span>
          </router-link>
        </div>

        <div class="nav-menu">
          <!-- <router-link to="/import" class="nav-link" v-slot="{ isActive }">
            <div class="nav-link-content" :class="{ active: isActive }">
              <i class="fas fa-cloud-upload-alt"></i>
              <span>导入</span>
            </div>
          </router-link> -->
          <router-link to="/grouping" class="nav-link" v-slot="{ isActive }">
            <div class="nav-link-content" :class="{ active: isActive }">
              <i class="fas fa-object-group"></i>
              <span>分组</span>
            </div>
          </router-link>
          <!-- <router-link to="/display" class="nav-link" v-slot="{ isActive }">
            <div class="nav-link-content" :class="{ active: isActive }">
              <i class="fas fa-images"></i>
              <span>展示</span>
            </div>
          </router-link> -->
          <router-link to="/export" class="nav-link" v-slot="{ isActive }">
            <div class="nav-link-content" :class="{ active: isActive }">
              <i class="fas fa-file-export"></i>
              <span>导出</span>
            </div>
          </router-link>
        </div>

        <div class="nav-footer">
          <button class="nav-link btn-clear" @click="handleClearCache" title="清除缓存">
            <div class="nav-link-content danger">
              <i class="fas fa-trash-alt"></i>
              <span>清除缓存</span>
            </div>
          </button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useApiStore } from './stores/api'
import { ElMessage } from 'element-plus'

const apiStore = useApiStore()

const handleClearCache = async () => {
  try {
    await apiStore.clearCache()
    ElMessage.success('缓存清除成功')
  } catch (error) {
    console.error('清除缓存失败:', error)
    ElMessage.error('清除缓存失败: ' + error.message)
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  background: var(--background-color);
}

.sidebar {
  width: 280px;
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 100;
  padding: 1rem;
}

.sidebar-content {
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.nav-brand {
  padding: 2rem;
}

.brand {
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #00a8ff, #00ff88);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 168, 255, 0.3);
}

.brand-text {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #2c3e50, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.nav-menu {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-link {
  text-decoration: none;
  padding: 0.5rem;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link-content {
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link-content:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.nav-link-content.active {
  background: linear-gradient(135deg, #00a8ff, #00ff88);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 168, 255, 0.3);
}

.nav-link-content.danger:hover {
  background: linear-gradient(135deg, #ff4757, #ff6b81);
  color: white;
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.3);
}

.nav-link i {
  font-size: 1.25rem;
  width: 1.5rem;
  text-align: center;
}

.nav-footer {
  padding: 1.5rem 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.4);
}

.btn-clear {
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 16px;
}

.main-content {
  flex: 1;
  margin-left: 280px;
  padding: 2rem;
  min-height: 100vh;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: relative;
    padding: 0.5rem;
  }

  .sidebar-content {
    border-radius: 16px;
  }

  .nav-brand {
    padding: 1rem;
  }

  .brand-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }

  .brand-text {
    font-size: 1.25rem;
  }

  .nav-menu {
    padding: 0.5rem;
  }

  .nav-link {
    padding: 0.25rem;
  }

  .nav-footer {
    padding: 1rem 0.5rem;
  }

  .main-content {
    margin-left: 0;
    padding: 1rem;
  }

  .app {
    flex-direction: column;
  }
}
</style>
