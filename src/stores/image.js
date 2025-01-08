import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useImageStore = defineStore('image', () => {
  const images = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 导入文件夹
  const importFolder = async (folderHandle) => {
    try {
      loading.value = true
      const newImages = []

      // 递归遍历文件夹
      const traverseFolder = async (handle, path = '') => {
        for await (const entry of handle.values()) {
          if (entry.kind === 'directory') {
            await traverseFolder(entry, `${path}${entry.name}/`)
          } else if (entry.kind === 'file') {
            const file = await entry.getFile()
            if (file.type.startsWith('image/')) {
              const imageData = {
                id: Date.now().toString() + Math.random().toString(36).slice(2),
                name: file.name,
                url: URL.createObjectURL(file),
                size: file.size,
                type: file.type,
                path: path,
                groupId: null,
                createdAt: new Date().toISOString(),
              }
              newImages.push(imageData)
            }
          }
        }
      }

      await traverseFolder(folderHandle)
      images.value = [...images.value, ...newImages]
      return newImages
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 添加图片
  const importImages = async (files) => {
    try {
      loading.value = true
      const newImages = await Promise.all(
        Array.from(files).map(async (file) => ({
          id: Date.now().toString() + Math.random().toString(36).slice(2),
          name: file.name,
          url: URL.createObjectURL(file),
          size: file.size,
          type: file.type,
          path: '',
          groupId: null,
          createdAt: new Date().toISOString(),
        })),
      )
      images.value = [...images.value, ...newImages]
      console.log('-----------', newImages)
      return newImages
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // 设置图片列表
  const setImages = (newImages) => {
    images.value = newImages
  }

  // 删除图片
  const deleteImages = async (imageIds) => {
    try {
      loading.value = true
      images.value = images.value.filter((img) => !imageIds.includes(img.id))
    } catch (error) {
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除单张图片
  const deleteImage = (imageId) => {
    return deleteImages([imageId])
  }

  // 更新图片
  const updateImage = (imageId, updates) => {
    const index = images.value.findIndex((img) => img.id === imageId)
    if (index !== -1) {
      images.value[index] = { ...images.value[index], ...updates }
    }
  }

  // 批量更新图片
  const updateImages = (imageIds, updates) => {
    imageIds.forEach((id) => updateImage(id, updates))
  }

  // 获取图片
  const getImageById = (id) => {
    return images.value.find((img) => img.id === id)
  }

  // 获取分组图片
  const getImagesByGroupId = (groupId) => {
    return images.value.filter((img) => img.groupId === groupId)
  }

  // 获取未分组图片
  const getUngroupedImages = () => {
    return images.value.filter((img) => !img.groupId)
  }

  // 移动图片到分组
  const moveImagesToGroup = async (imageIds, groupId) => {
    try {
      loading.value = true
      console.log(`Moving images ${imageIds} to group ${groupId}`)

      // 批量更新图片的分组ID
      imageIds.forEach((imageId) => {
        const index = images.value.findIndex((img) => img.id === imageId)
        if (index !== -1) {
          images.value[index] = {
            ...images.value[index],
            groupId: groupId,
            updatedAt: new Date().toISOString(),
          }
        }
      })

      console.log('Updated images:', images.value)
    } catch (error) {
      console.error('Error moving images:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  // 根据接口返回的分组信息自动分组
  const autoGroupImages = async (groupingResults) => {
    try {
      loading.value = true
      console.log('Auto grouping images with results:', groupingResults)

      // 清除所有图片的分组信息
      images.value.forEach((img) => {
        img.groupId = null
      })

      // 根据分组结果更新图片的分组ID
      for (const group of groupingResults) {
        await moveImagesToGroup(group.image_ids, group.group_id)
      }

      console.log('Finished auto grouping images:', images.value)
    } catch (error) {
      console.error('Error in auto grouping:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    images,
    loading,
    error,
    importImages,
    importFolder,
    setImages,
    deleteImage,
    deleteImages,
    updateImage,
    updateImages,
    getImageById,
    getImagesByGroupId,
    getUngroupedImages,
    moveImagesToGroup,
    autoGroupImages,
  }
})
