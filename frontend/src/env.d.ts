/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKEND_ADMINISTRATOR: string
  readonly VITE_BACKEND_NURSE: string
  readonly VITE_BACKEND_DOCTOR: string
  readonly VITE_BACKEND_CUSTOMER: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
