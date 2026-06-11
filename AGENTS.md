这是一个医疗信息系统，分为四个端：
- doctor: 医生端
- nurse: 护士端
- administrator: 管理端
- customer: 顾客端 (暂时不做这个)

还有：
- frontend: 前端
- deploy: 部署相关的文档

该系统基于一个 kafka 消息队列通讯，kafka 充当事件总线，各个端将自己的事件发送到上面，其他端作为消费者监听需要的事件处理，以做到多端联动的效果。事件的 schema 如下：
```python
id: Optional[int] = Field(default=None, sa_column=Column(BigInteger, primary_key=True))
trace_id: uuid.UUID = Field(index=True, nullable=False)
source: str = Field(sa_column=Column(String(20), nullable=False))
user_id: str = Field(sa_column=Column(String(50), nullable=False))
user_role: str = Field(sa_column=Column(String(20), nullable=False))
action_code: str = Field(sa_column=Column(String(30), nullable=False))
time: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column=Column(DateTime(timezone=True), nullable=False),
)
status: int = Field(sa_column=Column(SmallInteger, nullable=False))
target_id: str = Field(sa_column=Column(String(50), nullable=False))
target_role: str = Field(sa_column=Column(String(20), nullable=False))
payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
```

项目使用 uv，所以使用 `uv run` 而不是 `python` 命令，四个端的 HTTP 服务器都使用 FastAPI，ORM 均使用 SQLModel。

前端使用 pnpm, vite + vue3 + naiveui + pinia + vue-router

# 部署
目前部署在一个测试服务器，使用 rsync 来将本地文件同步到服务器上：
```
rsync -avz --exclude='/.git' --filter=':- .gitignore' /Users/qingyi/Documents/Workspace/PROJECT_HyMed_System/. ubuntu@119.29.163.179:compete_hospital
```

注意 rsync 时，source directory 中最后有一个点 `.`

服务器有 docker，可使用 docker 在 ./deploy 下调用./deploy.sh自动部署

已经配置SSH免密码，尽管调用就是了