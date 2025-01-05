<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">AI</span> 图像分组系统
        </h1>
        <p class="hero-subtitle">智能、高效的图片分类管理解决方案</p>
        <div class="hero-actions">
          <router-link to="/import" class="btn btn-primary">
            <i class="fas fa-cloud-upload-alt"></i>
            开始使用
          </router-link>
          <router-link to="/about" class="btn btn-outline">
            <i class="fas fa-info-circle"></i>
            了解更多
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="tech-grid">
          <div class="tech-item large" :style="{ backgroundImage: `url(${demoImages[0]})` }">
            <div class="tech-overlay">
              <div class="tech-info">
                <i class="fas fa-brain"></i>
                <span>AI Recognition</span>
              </div>
            </div>
          </div>
          <div class="tech-grid-small">
            <div 
              v-for="(image, i) in demoImages.slice(1, 5)" 
              :key="i"
              class="tech-item small"
              :style="{ backgroundImage: `url(${image})` }"
            >
              <div class="tech-overlay">
                <div class="tech-info">
                  <i :class="techIcons[i]"></i>
                  <span>{{ techLabels[i] }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="tech-decoration">
          <div class="tech-line"></div>
          <div class="tech-dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="(feature, index) in features" :key="index">
          <div class="feature-icon">
            <i :class="feature.icon"></i>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <div class="stat-card" v-for="(stat, index) in stats" :key="index">
        <div class="stat-number">{{ stat.number }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const features = ref([
  {
    icon: 'fas fa-cloud-upload-alt',
    title: '智能导入',
    description: '支持批量导入JPEG、PNG等格式图片，单次可处理1000张以上'
  },
  {
    icon: 'fas fa-brain',
    title: 'AI分类',
    description: '采用先进的AI算法，自动识别和分类人物图像'
  },
  {
    icon: 'fas fa-project-diagram',
    title: '灵活分组',
    description: '支持拖拽操作和快速筛选，轻松管理大量图片'
  },
  {
    icon: 'fas fa-file-export',
    title: '便捷导出',
    description: '支持多种格式导出，满足不同场景需求'
  }
])

const stats = ref([
  { number: '1M+', label: '处理图片' },
  { number: '99%', label: '识别准确率' },
  { number: '50+', label: '企业用户' }
])

const techIcons = [
  'fas fa-microchip',
  'fas fa-network-wired',
  'fas fa-code',
  'fas fa-database'
]

const techLabels = [
  'Deep Learning',
  'Neural Network',
  'Smart Analysis',
  'Big Data'
]

const demoImages = [
  'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800',  // 主图
  'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800',
  'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800',
  'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800',
  'https://images.unsplash.com/photo-1607799279861-4dd421887fb3?w=800'
]
</script>

<style scoped>
.home-container {
  padding: 2rem;
}

.hero-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4rem;
  gap: 2rem;
  min-height: 60vh;
}

.hero-content {
  flex: 1;
  max-width: 600px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.gradient-text {
  background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.5rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 1rem;
}

.hero-visual {
  flex: 1;
  position: relative;
  max-width: 600px;
  padding: 2rem;
}

.tech-grid {
  display: flex;
  gap: 1rem;
  position: relative;
  z-index: 2;
}

.tech-grid-small {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  flex: 1;
}

.tech-item {
  background-size: cover;
  background-position: center;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.tech-item.large {
  width: 240px;
  height: 360px;
}

.tech-item.small {
  aspect-ratio: 1;
}

.tech-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.7),
    rgba(0, 0, 0, 0.2)
  );
  opacity: 0;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-end;
  padding: 1.5rem;
}

.tech-item:hover .tech-overlay {
  opacity: 1;
}

.tech-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.tech-info {
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.tech-info i {
  font-size: 1.1rem;
}

.tech-decoration {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.tech-line {
  position: absolute;
  top: 10%;
  right: -20px;
  width: 3px;
  height: 80%;
  background: linear-gradient(
    to bottom,
    var(--primary-color),
    transparent
  );
  opacity: 0.3;
}

.tech-dots {
  position: absolute;
  top: 50%;
  right: -30px;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-color);
  opacity: 0.5;
}

.dot:nth-child(2) {
  opacity: 0.8;
}

.dot:nth-child(3) {
  opacity: 0.3;
}

@media (max-width: 1024px) {
  .tech-grid {
    flex-direction: column;
  }

  .tech-item.large {
    width: 100%;
    height: 280px;
  }
}

@media (max-width: 768px) {
  .hero-visual {
    padding: 1rem;
  }

  .tech-decoration {
    display: none;
  }
}

.section-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 3rem;
  color: var(--text-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.feature-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 2rem;
  text-align: center;
  box-shadow: var(--box-shadow);
  transition: var(--transition);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 1.5rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
  padding: 2rem;
  background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
  border-radius: var(--border-radius);
  color: white;
}

.stat-card {
  text-align: center;
  padding: 1.5rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
}

.btn-outline {
  background: transparent;
  border: 2px solid var(--primary-color);
  color: var(--primary-color);
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: var(--transition);
}

.btn-outline:hover {
  background: var(--primary-color);
  color: white;
}

@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    text-align: center;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .hero-actions {
    justify-content: center;
  }

  .tech-decoration {
    display: none;
  }
}

.demo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: var(--border-radius);
  transition: transform 0.3s ease;
}

.visual-item:hover .demo-image {
  transform: scale(1.05);
}
</style> 