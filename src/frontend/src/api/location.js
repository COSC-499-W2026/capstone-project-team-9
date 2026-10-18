import { post } from './client'

export const verifyLocation = (latitude, longitude) =>
  post('/location/verify', { latitude, longitude })