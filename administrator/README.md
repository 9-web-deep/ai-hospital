## 安装依赖（uv）

```bash
uv sync
```

## 运行服务

```bash
uv run uvicorn app.main:app --reload --port 8001
```

## 数据库与迁移（SQLModel + Alembic）

（生成迁移）：

```bash
export DATABASE_URL=sqlite+aiosqlite:///app.db
uv run alembic -c alembic.ini revision --autogenerate -m "init"
uv run alembic -c alembic.ini upgrade head
unset DATABASE_URL
```

也可以通过环境变量覆盖连接串：

```bash
export DATABASE_URL="postgresql+asyncpg://app:app123456@postgresql:5432/administrator_db"
uv run alembic -c alembic.ini upgrade head
```
