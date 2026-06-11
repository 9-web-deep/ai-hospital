Migrate（每个端使用自己的数据库，避免 Alembic 冲突）：

```shell
# nurse
DATABASE_URL="postgresql+asyncpg://app:app123456@postgresql:5432/nurse_db" uv run alembic -c alembic.ini upgrade head

# administrator
DATABASE_URL="postgresql+asyncpg://app:app123456@postgresql:5432/administrator_db" uv run alembic -c alembic.ini upgrade head

# doctor（如果后续引入表/迁移）
DATABASE_URL="postgresql+asyncpg://app:app123456@postgresql:5432/doctor_db" uv run alembic -c alembic.ini upgrade head
```

注意：`deploy/postgres_init/` 下的建库脚本只会在 `./postgres_data` 第一次初始化时执行；如果你之前已经启动过旧的单库版本，需要删除 `deploy/postgres_data`（或手动创建 `nurse_db` / `administrator_db`）再重启。

Kafka 初始化（创建/配置 topic，并设置 24h 清理）

本项目事件总线使用的 topic 为：`event_bus`。

启动后（`cd deploy && sudo docker compose up -d`），执行：

```shell
# 1) 创建 topic（若已存在会报错，可跳过）
sudo docker exec -it kafka kafka-topics.sh \
  --bootstrap-server kafka:9092 \
  --create --if-not-exists \
  --topic event_bus \
  --partitions 1 \
  --replication-factor 1 \
  --config cleanup.policy=delete \
  --config retention.ms=86400000 \
  --config segment.ms=3600000

# 2) 若 topic 已经自动创建过，用 alter 覆盖配置（推荐再执行一次，确保生效）
sudo docker exec -it kafka kafka-configs.sh \
  --bootstrap-server kafka:9092 \
  --entity-type topics \
  --entity-name event_bus \
  --alter \
  --add-config cleanup.policy=delete,retention.ms=86400000,segment.ms=3600000
```

说明：
- `retention.ms=86400000`：消息保留 24 小时后可被清理
- Kafka 清理是按 log segment 做删除的，所以建议配 `segment.ms=3600000`（1 小时切分一次），避免“超过 24h 但还没清掉”的体感延迟
