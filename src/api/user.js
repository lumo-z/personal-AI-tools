import { request } from '@/utils/request.js'
// 登录接口
export function loginApi (data) {
  request({
    url: 'api/login',
    method: 'post',
    data: data
  }).then(res => {
    localStorage.setItem('token', res.data.token)
    return {
      user: res.data.user,
      token: res.data.token
    }
  }).catch(err => {
    console.log(err)
  })
}
export function registerApi (data) {
  request({
    url: 'api/register',
    method: 'post',
    data: data
  })
}
