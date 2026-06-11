FROM node:20-alpine AS build

WORKDIR /app

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY frontend/ ./

ARG VITE_BACKEND_ADMINISTRATOR=/api/administrator
ARG VITE_BACKEND_NURSE=/api/nurse
ARG VITE_BACKEND_DOCTOR=/api/doctor
ARG VITE_BACKEND_CUSTOMER=/api/customer

ENV VITE_BACKEND_ADMINISTRATOR=$VITE_BACKEND_ADMINISTRATOR
ENV VITE_BACKEND_NURSE=$VITE_BACKEND_NURSE
ENV VITE_BACKEND_DOCTOR=$VITE_BACKEND_DOCTOR
ENV VITE_BACKEND_CUSTOMER=$VITE_BACKEND_CUSTOMER

RUN pnpm build

FROM nginx:1.27

COPY deploy/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY deploy/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html
