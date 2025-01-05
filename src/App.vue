<template>
  <div class="app-container">
    <!-- 导航栏 -->
    <nav class="navigation">
      <div class="nav-content">
        <div class="nav-brand">
          <div class="brand-logo">
            <i class="fas fa-layer-group"></i>
          </div>
          <div class="brand-text">
            <span class="brand-highlight">AI</span>
            <span class="brand-normal">VISION</span>
          </div>
        </div>
        
        <div class="nav-links">
          <router-link to="/" class="nav-item" title="首页">
            <i class="fas fa-home"></i>
            <span>HOME</span>
          </router-link>
          <router-link to="/import" class="nav-item" title="导入">
            <i class="fas fa-cloud-upload-alt"></i>
            <span>IMPORT</span>
          </router-link>
          <router-link to="/grouping" class="nav-item" title="分组">
            <i class="fas fa-object-group"></i>
            <span>GROUP</span>
          </router-link>
          <router-link to="/display" class="nav-item" title="展示">
            <i class="fas fa-th"></i>
            <span>DISPLAY</span>
          </router-link>
          <router-link to="/export" class="nav-item" title="导出">
            <i class="fas fa-file-export"></i>
            <span>EXPORT</span>
          </router-link>
        </div>

        <div class="nav-actions">
          <div class="search-bar">
            <i class="fas fa-search"></i>
            <input type="text" placeholder="搜索...">
          </div>
          
          <!-- 通知菜单 -->
          <div class="notification-menu">
            <button class="btn-icon" @click="toggleNotifications" title="通知">
              <i class="fas fa-bell"></i>
              <span v-if="unreadNotifications.length" class="notification-badge">
                {{ unreadNotifications.length }}
              </span>
            </button>
            
            <!-- 通知下拉面板 -->
            <div class="dropdown-panel" v-show="showNotifications">
              <div class="panel-header">
                <h3>通知</h3>
                <button class="btn-text" @click="markAllAsRead">
                  全部已读
                </button>
              </div>
              <div class="notification-list">
                <div 
                  v-for="notice in notifications" 
                  :key="notice.id"
                  class="notification-item"
                  :class="{ unread: !notice.read }"
                >
                  <div class="notice-icon">
                    <i :class="notice.icon"></i>
                  </div>
                  <div class="notice-content">
                    <div class="notice-title">{{ notice.title }}</div>
                    <div class="notice-desc">{{ notice.description }}</div>
                    <div class="notice-time">{{ notice.time }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 用户菜单 -->
          <div class="user-menu">
            <div class="user-trigger" @click="toggleUserMenu">
              <img 
                src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=b6e3f4" 
                alt="用户头像" 
                class="avatar"
              >
            </div>
            
            <!-- 用户下拉菜单 -->
            <div class="dropdown-panel" v-show="showUserMenu">
              <div class="user-info">
                <img 
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix&backgroundColor=b6e3f4" 
                  alt="用户头像" 
                  class="avatar-large"
                >
                <div class="user-details">
                  <div class="user-name">测试用户</div>
                  <div class="user-email">user@example.com</div>
                </div>
              </div>
              <div class="menu-items">
                <a href="#" class="menu-item">
                  <i class="fas fa-user"></i>
                  个人信息
                </a>
                <a href="#" class="menu-item">
                  <i class="fas fa-cog"></i>
                  系统设置
                </a>
                <div class="divider"></div>
                <a href="#" class="menu-item text-danger">
                  <i class="fas fa-sign-out-alt"></i>
                  退出登录
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 路由视图 -->
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
import { ref, computed } from 'vue'

const showNotifications = ref(false)
const showUserMenu = ref(false)

const notifications = ref([
  {
    id: 1,
    title: '系统更新',
    description: '系统已更新到最新版本 v1.2.0',
    time: '10分钟前',
    icon: 'fas fa-sync',
    read: false
  },
  {
    id: 2,
    title: '处理完成',
    description: '批量图片处理已完成',
    time: '1小时前',
    icon: 'fas fa-check-circle',
    read: false
  }
])

const unreadNotifications = computed(() => 
  notifications.value.filter(n => !n.read)
)

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showNotifications.value = false
}

const markAllAsRead = () => {
  notifications.value.forEach(notice => {
    notice.read = true
  })
}
</script>

<style>
:root {
  --primary-color: #00a8ff;
  --secondary-color: #192a56;
  --accent-color: #0097e6;
  --background-color: #f1f2f6;
  --surface-color: #ffffff;
  --text-primary: #2f3542;
  --text-secondary: #57606f;
  --success-color: #2ed573;
  --error-color: #ff4757;
  --border-radius: 12px;
  --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--background-color);
  color: var(--text-primary);
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navigation {
  background: rgba(255, 255, 255, 0.95);
  height: 70px;
  padding: 0;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.nav-content {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-logo {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  box-shadow: 0 4px 15px rgba(33, 147, 176, 0.3);
}

.brand-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.brand-highlight {
  background: linear-gradient(135deg, #2193b0, #6dd5ed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
}

.brand-normal {
  color: var(--text-primary);
  opacity: 0.9;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 0.25rem;
  margin: 0 2rem;
  height: 100%;
}

.nav-item {
  text-decoration: none;
  color: var(--text-secondary);
  padding: 0 1.5rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  height: 100%;
  position: relative;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0.75;
}

.nav-item i {
  font-size: 1.1rem;
  transition: transform 0.3s ease;
  opacity: 0.8;
}

.nav-item:hover {
  opacity: 1;
}

.nav-item.router-link-active {
  color: var(--primary-color);
  opacity: 1;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  transition: all 0.3s ease;
  transform: translateX(-50%);
  border-radius: 3px 3px 0 0;
}

.nav-item:hover::after {
  width: 30px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--background-color);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.search-bar:focus-within {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-bar input {
  border: none;
  background: none;
  outline: none;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  width: 180px;
  color: var(--text-secondary);
  opacity: 0.9;
}

.search-bar input::placeholder {
  color: var(--text-secondary);
  opacity: 0.5;
  letter-spacing: 0.5px;
}

.search-bar i {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.btn-icon {
  position: relative;
  width: 40px;
  height: 40px;
  border: none;
  background: var(--background-color);
  color: var(--text-secondary);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: white;
  color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: var(--error-color);
  color: white;
  font-size: 0.7rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  font-weight: 600;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid var(--primary-color);
  transition: all 0.3s ease;
  cursor: pointer;
}

.avatar:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 168, 255, 0.2);
}

@media (max-width: 768px) {
  .navigation {
    height: 60px;
  }

  .nav-content {
    padding: 0 1rem;
  }

  .brand-text,
  .nav-item span,
  .search-bar {
    display: none;
  }

  .nav-links {
    margin: 0;
    gap: 0;
  }

  .nav-item {
    padding: 0 1rem;
  }

  .btn-icon {
    width: 35px;
    height: 35px;
  }

  .avatar {
    width: 35px;
    height: 35px;
  }
}

/* 更新主内容区域的高度 */
.main-content {
  min-height: calc(100vh - 70px);
}

@media (max-width: 768px) {
  .main-content {
    min-height: calc(100vh - 60px);
  }
}

/* 动画过渡 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局按钮样式 */
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-color);
  transform: translateY(-2px);
}

/* 全局卡片样式 */
.card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
  transition: var(--transition);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

/* 全局输入框样式 */
.input {
  padding: 0.75rem 1rem;
  border: 2px solid #e1e1e1;
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: var(--transition);
  width: 100%;
}

.input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 168, 255, 0.1);
}

.dropdown-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 300px;
  z-index: 1000;
}

.panel-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--background-color);
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 1rem;
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid var(--background-color);
  transition: var(--transition);
}

.notification-item:hover {
  background: var(--background-color);
}

.notification-item.unread {
  background: rgba(0, 168, 255, 0.05);
}

.notice-icon {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  background: var(--background-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.notice-content {
  flex: 1;
}

.notice-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.notice-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.notice-time {
  font-size: 0.8rem;
  color: var(--text-secondary);
  opacity: 0.8;
}

.user-info {
  padding: 1rem;
  display: flex;
  gap: 1rem;
  border-bottom: 1px solid var(--background-color);
}

.avatar-large {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius);
}

.user-details {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.user-name {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.user-email {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.menu-items {
  padding: 0.5rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  text-decoration: none;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.menu-item:hover {
  background: var(--background-color);
}

.menu-item i {
  width: 20px;
  opacity: 0.8;
}

.divider {
  height: 1px;
  background: var(--background-color);
  margin: 0.5rem 0;
}

.text-danger {
  color: var(--error-color);
}

.text-danger:hover {
  background: rgba(255, 71, 87, 0.1);
}
</style>
