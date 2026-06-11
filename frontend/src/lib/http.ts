import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export const adminHttp = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_ADMINISTRATOR,
  timeout: 10000,
})

export const doctorHttp = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_DOCTOR,
  timeout: 180000,
})

export const nurseHttp = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_NURSE,
  timeout: 180000,
})

export default http
