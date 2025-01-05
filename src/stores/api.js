import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useApiStore = defineStore('api', () => {
  const loading = ref(false)
  const error = ref(null)
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  // 配置 axios 实例
  const api = axios.create({
    baseURL,
    timeout: 120000,
  })

  // 上传图片
  const uploadImages = async (files) => {
    try {
      loading.value = true
      const formData = new FormData()
      files.forEach((file) => {
        formData.append('files', file)
      })

      const response = await api.post('/api/images/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取图片列表
  const getImages = async () => {
    try {
      loading.value = true
      const response = await api.get('/api/images')
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取图片信息
  const getImage = async (imageId) => {
    try {
      loading.value = true
      const { data: response } = await api.get(`/api/images/${imageId}`)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除图片
  const deleteImage = async (imageId) => {
    try {
      loading.value = true
      const response = await api.delete(`/api/images/${imageId}`)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 智能分组
  const groupImages = async (imageIds, similarityThreshold = 0.55) => {
    try {
      loading.value = true
      const response = await api.post('/api/images/group', {
        image_ids: imageIds,
        similarity_threshold: similarityThreshold,
      })
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 创建分组
  const createGroup = async (group) => {
    try {
      loading.value = true
      const response = await api.post('/api/groups', {
        id: group.id,
        name: group.name,
        description: group.description,
        image_ids: group.image_ids || [],
        created_at: group.created_at,
        updated_at: group.updated_at,
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取所有分组
  const getGroups = async () => {
    try {
      loading.value = true
      const response = await api.get('/api/groups')
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 更新分组
  const updateGroup = async (groupId, group) => {
    try {
      loading.value = true
      const response = await api.put(`/api/groups/${groupId}`, {
        id: groupId,
        name: group.name,
        description: group.description,
        image_ids: group.image_ids || [],
        created_at: group.created_at,
        updated_at: new Date().toISOString(),
      })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 删除分组
  const deleteGroup = async (groupId) => {
    try {
      loading.value = true
      const response = await api.delete(`/api/groups/${groupId}`)
      return response
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    baseURL,
    uploadImages,
    getImages,
    getImage,
    deleteImage,
    groupImages,
    createGroup,
    getGroups,
    updateGroup,
    deleteGroup,
  }
})
