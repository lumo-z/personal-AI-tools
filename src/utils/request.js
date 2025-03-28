import axios from 'axios'
import router from '@/router'
import store from '@/store'
export const request = axios.create({
  baseURL: 'http://localhost:5000'
})
// 添加请求拦截器
request.interceptors.request.use(config => {
  const token = store.getters['user/token']
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 添加响应拦截器处理401错误
request.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.dispatch('user/logout')
      if (error.response.data.shouldRedirect) {
        router.push('/')
      }
    }
    return Promise.reject(error)
  }
)
