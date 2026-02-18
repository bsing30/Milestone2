# ============================================
# Builder stage - install dependencies only
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy dependency list first (best layer caching - changes least often)
COPY app/requirements.txt .

# Install dependencies to user directory (no dev deps in runtime)
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

# ============================================
# Runtime stage - minimal production image
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Non-root user for security (minimal attack surface)
RUN useradd --create-home --shell /bin/bash appuser

# Copy packages to appuser's home (root cannot be read by appuser)
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app/ .

RUN chown -R appuser:appuser /home/appuser /app

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 8080

ENV PORT=8080

CMD ["python", "app.py"]
