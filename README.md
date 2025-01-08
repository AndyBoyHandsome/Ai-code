# 人脸分组应用

一个基于人脸识别的图片分组应用，使用 Vue.js 和 FastAPI 构建。

## 功能特点

- 自动人脸检测和分组
- 支持拖拽管理分组
- 批量导入和导出
- 实时预览和编辑
- 响应式设计

## 部署说明

### 使用 Docker 部署（推荐）

1. 确保已安装 Docker 和 Docker Compose

   ```bash
   # Windows 用户可以从以下地址下载 Docker Desktop
   # https://www.docker.com/products/docker-desktop
   ```

2. 克隆项目

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

3. 构建和启动服务

   ```bash
   docker-compose up -d --build
   ```

4. 访问应用
   - 前端界面：http://localhost
   - API 文档：http://localhost:8000/docs

### 手动部署

#### 后端

1. 安装 Python 3.9+ 和依赖

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 启动服务
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

#### 前端

1. 安装 Node.js 16+ 和依赖

   ```bash
   npm install
   ```

2. 构建生产版本

   ```bash
   npm run build
   ```

3. 使用 nginx 或其他 Web 服务器部署 dist 目录

## 注意事项

- 确保 uploads 目录有写入权限
- 建议使用 SSD 存储以获得更好的性能
- Windows 用户需要确保 Docker Desktop 已启用 WSL 2 后端

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

# Ai-code
