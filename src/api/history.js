import { request } from '@/utils/request'
export function SaveHistoryApi (data) {
  return request({
    url: '/api/records',
    method: 'POST',
    data,
    timeout: 100000
  })
}
export function GetHistoryApi (userId) {
  return request({
    url: '/api/sessions',
    method: 'GET',
    params: userId,
    timeout: 100000
  })
}

export function GetDetailHistoryApi (params) {
  return request({
    url: '/api/records',
    method: 'GET',
    params, // params: { userId: userId, sessionId: sessionId}
    timeout: 100000
  })
}
