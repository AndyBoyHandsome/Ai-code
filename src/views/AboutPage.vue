<template>
  <div class="about-container">
    <div class="page-header">
      <h1>关于我们</h1>
      <p class="subtitle">了解更多关于 AI Vision 的信息</p>
    </div>

    <div class="about-content">
      <div class="about-section card">
        <div class="section-header">
          <i class="fas fa-rocket"></i>
          <h2>产品介绍</h2>
        </div>
        <p>AI Vision 是一款基于人工智能的图像分组管理系统，致力于为用户提供智能、高效的图片分类解决方案。通过先进的深度学习算法，系统能够自动识别和分类图片中的人物，大幅提高工作效率。</p>
      </div>

      <div class="features-grid">
        <div class="feature-card" v-for="feature in features" :key="feature.title">
          <div class="feature-icon">
            <i :class="feature.icon"></i>
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>

      <div class="about-section card">
        <div class="section-header">
          <i class="fas fa-chart-line"></i>
          <h2>技术优势</h2>
        </div>
        <div class="tech-advantages">
          <div class="tech-item" v-for="tech in techAdvantages" :key="tech.title">
            <div class="tech-icon">
              <i :class="tech.icon"></i>
            </div>
            <div class="tech-content">
              <h4>{{ tech.title }}</h4>
              <p>{{ tech.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="contact-section card">
        <div class="section-header">
          <i class="fas fa-envelope"></i>
          <h2>联系我们</h2>
        </div>
        <div class="contact-info">
          <div class="contact-item">
            <i class="fas fa-envelope"></i>
            <span>support@aivision.com</span>
          </div>
          <div class="contact-item">
            <i class="fas fa-phone"></i>
            <span>400-123-4567</span>
          </div>
          <div class="contact-item">
            <i class="fas fa-map-marker-alt"></i>
            <span>北京市海淀区科技园区</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const features = [
  {
    icon: 'fas fa-brain',
    title: '智能识别',
    description: '采用最新的深度学习算法，准确识别图片中的人物特征。'
  },
  {
    icon: 'fas fa-bolt',
    title: '高效处理',
    description: '支持批量处理，单次可处理上千张图片，效率提升数十倍。'
  },
  {
    icon: 'fas fa-shield-alt',
    title: '安全可靠',
    description: '采用多重加密技术，确保数据安全，支持私有化部署。'
  }
]

const techAdvantages = [
  {
    icon: 'fas fa-microchip',
    title: '深度学习算法',
    description: '使用最新的深度学习模型，识别准确率达到99%以上。'
  },
  {
    icon: 'fas fa-database',
    title: '海量数据处理',
    description: '优化的数据处理流程，轻松应对TB级数据量。'
  },
  {
    icon: 'fas fa-cloud',
    title: '云端部署',
    description: '支持云端部署和本地部署，灵活满足不同需求。'
  }
]
</script>

<style scoped>
.about-container {
  padding: 2rem;
}

.about-content {
  max-width: 1200px;
  margin: 0 auto;
}

.about-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section-header i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.section-header h2 {
  font-size: 1.8rem;
  margin: 0;
  color: var(--text-primary);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

.tech-advantages {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tech-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--background-color);
  border-radius: var(--border-radius);
}

.tech-icon {
  font-size: 2rem;
  color: var(--primary-color);
}

.tech-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
}

.tech-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.contact-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--background-color);
  border-radius: var(--border-radius);
}

.contact-item i {
  font-size: 1.2rem;
  color: var(--primary-color);
}

@media (max-width: 768px) {
  .about-container {
    padding: 1rem;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .contact-info {
    grid-template-columns: 1fr;
  }
}
</style> 