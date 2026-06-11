## Nurse 服务说明

## 安装依赖（uv）

```bash
uv sync
```

## 运行服务

```bash
uv run uvicorn app.main:app --reload --port 8002
```

## 数据库与迁移（SQLModel + Alembic）

（生成迁移）：

```bash
uv run alembic -c alembic.ini revision --autogenerate -m "init"
uv run alembic -c alembic.ini upgrade head
```

也可以通过环境变量覆盖连接串：

```bash
export DATABASE_URL="sqlite+aiosqlite:////absolute/path/to/app.db"
```

PostgreSQL 示例（部署 / docker-compose 默认库名为 `nurse_db`）：

```bash
export DATABASE_URL="postgresql+asyncpg://app:app123456@postgresql:5432/nurse_db"
uv run alembic -c alembic.ini upgrade head
```
