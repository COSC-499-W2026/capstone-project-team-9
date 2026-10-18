import { get } from './client'

export const checkHealth = () => get('/health')