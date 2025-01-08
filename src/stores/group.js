import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApiStore } from './api'

export const useGroupStore = defineStore('group', () => {
  const apiStore = useApiStore()
  const groups = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 创建分组
  const createGroup = async (groupData) => {
    try {
      loading.value = true
      const newGroup = {
        id: Date.now().toString(),
        name: groupData.name,
        description: groupData.description,
        image_ids: groupData.image_ids || [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      console.log('***************')
      console.log('recevice groupData:', groupData) // 打印创建的分组
      console.log('Creating group:', newGroup) // 打印创建的分组
      console.log('***************')
      const createdGroup = await apiStore.createGroup(newGroup)
      groups.value.push(createdGroup)
      return createdGroup
    } catch (error) {
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  // 批量创建分组
  const createGroups = async (groupsData) => {
    try {
      loading.value = true
      const newGroups = groupsData.map((data) => ({
        id: Date.now().toString() + Math.random().toString(36).slice(2),
        ...data,
        createdAt: new Date().toISOString(),
      }))
      groups.value.push(...newGroups)
      return newGroups
    } catch (error) {
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新分组
  const updateGroup = async (groupData) => {
    try {
      loading.value = true
      const index = groups.value.findIndex((g) => g.id === groupData.id)
      if (index !== -1) {
        const updatedGroup = await apiStore.updateGroup(groupData.id, {
          ...groups.value[index],
          ...groupData,
          updated_at: new Date().toISOString(),
        })
        groups.value[index] = updatedGroup
        return updatedGroup
      }
    } catch (error) {
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  // 删除分组
  const deleteGroup = async (groupId) => {
    try {
      loading.value = true
      groups.value = groups.value.filter((g) => g.id !== groupId)
    } catch (error) {
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取分组
  const getGroupById = (id) => {
    return groups.value.find((group) => group.id === id)
  }

  // 获取分组名称
  const getGroupName = (id) => {
    const group = getGroupById(id)
    return group ? group.name : '未分组'
  }

  // 设置分组列表
  const setGroups = (newGroups) => {
    groups.value = newGroups
  }

  // 清空所有分组
  const clearGroups = () => {
    groups.value = []
  }

  // 根据接口返回的分组信息创建分组
  const createGroupsFromResults = async (groupingResults) => {
    try {
      loading.value = true
      console.log('Creating groups from results:', groupingResults)

      // 清空现有分组
      clearGroups()

      // 直接使用后端返回的分组结果创建分组
      const newGroups = groupingResults.map((result) => ({
        id: result.group_id,
        name: result.name,
        description: `自动创建的分组 ${result.name}`,
        image_ids: result.image_ids,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }))

      // 添加新分组
      groups.value = newGroups
      console.log('Created groups:', groups.value)

      return groups.value
    } catch (error) {
      console.error('Error creating groups:', error)
      error.value = error.message
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    groups,
    loading,
    error,
    createGroup,
    createGroups,
    updateGroup,
    deleteGroup,
    getGroupById,
    getGroupName,
    setGroups,
    clearGroups,
    createGroupsFromResults,
  }
})
