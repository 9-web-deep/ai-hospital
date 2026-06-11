# Use a Python image with uv pre-installed
FROM docker.1ms.run/astral/uv:python3.13-alpine AS build

# Optional: set apk mirror for faster builds in China
ARG APK_MIRROR=
RUN if [ -n "$APK_MIRROR" ]; then \
      sed -i "s#https\\?://dl-cdn.alpinelinux.org/alpine#${APK_MIRROR}#g" /etc/apk/repositories; \
    fi

# Build deps for native extensions (greenlet, asyncpg etc.)
RUN apk add --no-cache build-base libffi-dev zlib-dev

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1

# Optional: PyPI mirror for uv/pip (e.g. https://pypi.tuna.tsinghua.edu.cn/simple)
ARG UV_DEFAULT_INDEX=
ARG UV_EXTRA_INDEX_URL=
ENV UV_DEFAULT_INDEX=${UV_DEFAULT_INDEX}
ENV UV_EXTRA_INDEX_URL=${UV_EXTRA_INDEX_URL}
# Some environments/tools still read pip-style vars
ENV PIP_INDEX_URL=${UV_DEFAULT_INDEX}
ENV PIP_EXTRA_INDEX_URL=${UV_EXTRA_INDEX_URL}

# Install deps first (better cache)
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy application code
COPY hymed_no_kafka ./hymed_no_kafka
COPY main.py ./main.py
COPY README.md ./README.md

# Final sync to include the project itself (editable not needed in image)
RUN uv sync --no-dev


FROM python:3.13-alpine AS runtime

WORKDIR /app

# Optional: set apk mirror for faster builds in China
ARG APK_MIRROR=
RUN if [ -n "$APK_MIRROR" ]; then \
      sed -i "s#https\\?://dl-cdn.alpinelinux.org/alpine#${APK_MIRROR}#g" /etc/apk/repositories; \
    fi

# Runtime deps (asyncpg needs libpq)
RUN apk add --no-cache libpq libstdc++

COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/hymed_no_kafka /app/hymed_no_kafka
COPY --from=build /app/main.py /app/main.py

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
