# no_kafka（三合一缝合版）

把 `administrator`、`nurse`、`doctor` 三个服务“缝合”成单一 FastAPI 应用：

- Kafka -> 进程内全局 `asyncio.Queue`
- API 统一前缀：`/api/{nurse,administrator,doctor}/...`

## 启动

在 `experiment/no_kafka` 目录下：

`uvicorn main:app --reload`

## Docker 一键部署（POC）

在 `experiment/no_kafka` 目录下：

`docker compose up -d --build`

## Nginx（用于压测对齐 deploy）

`docker compose up -d --build` 后，可通过 Nginx 访问（推荐用于压测，以与 `deploy` 的入口保持一致）：

- Nginx 入口：`http://localhost:18082`
- API：`http://localhost:18082/api/{nurse,administrator,doctor}/...`

## 关键端点

- 护士端：`/api/nurse/...`
- 医生端：`/api/doctor/...`
- 管理端：`/api/administrator/...`
