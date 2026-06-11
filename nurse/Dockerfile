# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS build

# Optional: set apk mirror for faster builds in China
ARG APK_MIRROR=
RUN if [ -n "$APK_MIRROR" ]; then \
      sed -i "s#https\\?://dl-cdn.alpinelinux.org/alpine#${APK_MIRROR}#g" /etc/apk/repositories; \
    fi

# Install build dependencies for native extensions (greenlet, asyncpg etc.)
RUN apk add --no-cache build-base libffi-dev zlib-dev

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Optional: PyPI mirror for uv/pip (e.g. https://pypi.tuna.tsinghua.edu.cn/simple)
ARG UV_DEFAULT_INDEX=
ARG UV_EXTRA_INDEX_URL=
ENV UV_DEFAULT_INDEX=${UV_DEFAULT_INDEX}
ENV UV_EXTRA_INDEX_URL=${UV_EXTRA_INDEX_URL}
ENV PIP_INDEX_URL=${UV_DEFAULT_INDEX}
ENV PIP_EXTRA_INDEX_URL=${UV_EXTRA_INDEX_URL}

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies into a cache-friendly location
RUN uv sync --frozen --no-dev --no-install-project

# Now copy the project itself
COPY . .

# Run the final sync to include the project
RUN uv sync --frozen --no-dev


# Final image
FROM python:3.13-alpine AS runtime

WORKDIR /app

# Optional: set apk mirror for faster builds in China
ARG APK_MIRROR=
RUN if [ -n "$APK_MIRROR" ]; then \
      sed -i "s#https\\?://dl-cdn.alpinelinux.org/alpine#${APK_MIRROR}#g" /etc/apk/repositories; \
    fi

# Install necessary runtime dependencies
RUN apk add --no-cache libpq libstdc++

# Copy the virtual environment and application code
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/app /app/app
COPY --from=build /app/alembic /app/alembic
COPY --from=build /app/alembic.ini /app/alembic.ini

# Use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose the application port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
