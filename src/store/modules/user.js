import { request } from '@/utils/request'
export default {
  namespaced: true,
  state: {
    user: JSON.parse(localStorage.getItem('user') || 'null'), // 从localStorage初始化
    token: localStorage.getItem('token'), // 从localStorage初始化
    isAuthenticated: !!localStorage.getItem('token') // 从token判断
  },
  mutations: {
    SET_USER (state, payload) {
      state.user = payload.user
      state.token = payload.token
      state.isAuthenticated = !!payload.user
      localStorage.setItem('token', payload.token)
      localStorage.setItem('user', JSON.stringify(payload.user)) // 新增用户信息持久化
    },
    CLEAR_USER (state) {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    }
  },
  actions: {
    async login ({ commit }, { username, password }) {
      try {
        const response = await request.post('/api/login', { username, password })
        if (response.data.code === 200) {
          const { token, user } = response.data.data
          commit('SET_USER', { token, user })
          return { success: true, user }
        } else {
          return {
            success: false,
            error: response.data.message || '登录失败'
          }
        }
      } catch (error) {
        console.error('登录失败:', error)
        return {
          success: false,
          error: error.response?.data?.error || '网络错误'
        }
      }
    },
    logout ({ commit }) {
      commit('CLEAR_USER')
    }
  },
  getters: {
    user: (state) => state.user,
    isAuthenticated: (state) => state.isAuthenticated,
    token: (state) => state.token
  }
}
