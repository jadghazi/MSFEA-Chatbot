# PLACEHOLDER — deployment is finalized in Phase 10 (CLAUDE.md §5.10). This is a
# minimal, runnable skeleton so the shape is real; it will grow as the app does.
FROM python:3.11-slim

WORKDIR /app

# Install the package (dependencies come from pyproject.toml).
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

EXPOSE 8000

# Config is provided at runtime via environment variables (never baked in, §3).
CMD ["uvicorn", "msfea_bot.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
