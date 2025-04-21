import { request } from '@/utils/request'

export function askApi (data) {
  return request({
    url: '/api/ask',
    method: 'post',
    data,
    timeout: 100000
  }).then(response => {
    return response.data ? response : Promise.reject(new Error('无效响应'))
  })
}
