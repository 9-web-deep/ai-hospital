# AI Hospital

AI Hospital is a multi-service medical system prototype. The project contains separate backend services for administrator, doctor, nurse, and customer scenarios, plus a Vue-based frontend and deployment files.

## Project Structure

```text
ai-hospital/
|-- administrator/   # Administrator backend service
|-- customer/        # Customer-facing backend service
|-- doctor/          # Doctor backend service
|-- nurse/           # Nurse backend service
|-- frontend/        # Vue frontend application
|-- deploy/          # Docker Compose, Nginx, PostgreSQL, and Kafka deployment files
|-- experiment/      # Experimental and stress-test versions
|-- AGENTS.md        # Development notes
`-- README.md        # Project overview
```

## Main Modules

- `administrator`: provides administrator-side APIs such as health checks and operation journal features.
- `doctor`: provides doctor-side APIs and AI-related service integration.
- `nurse`: provides nurse-side APIs, infusion tasks, dispensing tasks, and chat-related features.
- `customer`: provides customer-side service examples and health endpoints.
- `frontend`: provides the web interface built with Vue, TypeScript, Vite, Pinia, Vue Router, Vue I18n, Axios, and Naive UI.
- `deploy`: contains deployment scripts and service orchestration configuration.

## Frontend

The frontend source code is located in `frontend/`.

Common commands:

```bash
cd frontend
pnpm install
pnpm dev
pnpm build
```

## Backend Services

Each backend service is organized as an independent Python service. Service-specific files and instructions are placed inside their own directories:

- `administrator/`
- `doctor/`
- `nurse/`
- `customer/`

The project also includes Alembic migration files and Docker-related configuration for selected services.

## Deployment

Deployment-related files are located in `deploy/`, including:

- `docker-compose.yml`
- Nginx configuration
- PostgreSQL initialization scripts
- service deployment scripts

## Repository

This repository was initialized as a clean project upload for:

```text
https://github.com/9-web-deep/ai-hospital
```
