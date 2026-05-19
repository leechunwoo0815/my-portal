import api from './client'

export const achievementApi = {
  list() {
    return api.get('/v1/achievement/')
  },
  getMy() {
    return api.get('/v1/achievement/my')
  },
  getByCode(code: string) {
    return api.get(`/v1/achievement/${code}`)
  },
  check() {
    return api.post('/v1/achievement/check')
  },
}

export const checkinApi = {
  doCheckin() {
    return api.post('/v1/checkin/')
  },
  getStatus() {
    return api.get('/v1/checkin/status')
  },
  getCalendar(year: number, month: number) {
    return api.get('/v1/checkin/calendar', { params: { year, month } })
  },
  getRanking() {
    return api.get('/v1/checkin/ranking')
  },
}
