# syntax=docker/dockerfile:1
#
# Production image for the MSFEA CDC chatbot API (CLAUDE.md §3, §5.10).
# Design goals: portable (builds on x86_64 and Apple-Silicon/arm64), offline at
# runtime (models baked in — safe behind AUB's firewall), reproducible, non-root.

FROM python:3.12-slim AS production

# Fail-fast Python, no bytecode/pip cache, and a fixed model-cache path so the
# models baked below are found at runtime.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/opt/models/huggingface

WORKDIR /app

# --- CPU-only PyTorch --------------------------------------------------------
# The default torch wheel bundles ~2 GB of CUDA/GPU libraries we never use
# (embeddings run on CPU). Installing the CPU build first cuts the download ~10x
# and shrinks the final image by well over a gigabyte. Cached independently of
# the app code below.
COPY pyproject.toml ./
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# --- Dependencies ------------------------------------------------------------
# Install from pyproject *before* copying source. A code-only edit must not
# invalidate the expensive language/embedding-model layer below. `tomllib` is in
# Python 3.12, so this adds no build dependency and keeps pyproject as the single
# dependency source of truth.
RUN python - <<'PY'
import subprocess
import sys
import tomllib

with open("pyproject.toml", "rb") as f:
    project = tomllib.load(f)["project"]
dependencies = [*project["dependencies"], *project["optional-dependencies"]["gemini"]]
subprocess.check_call([sys.executable, "-m", "pip", "install", *dependencies])
PY

# Do not ship the vulnerable packaging-tool versions bundled by the base image.
# Keep this before model/source/content layers so normal edits reuse the result.
RUN pip install --upgrade pip==26.2 setuptools==83.0.0

# --- Bake models so the container needs NO internet at runtime ---------------
# Fast startup and firewall-safe. Override at build time with
# --build-arg EMBEDDING_MODEL=... if you change the default embedding model.
# The revision MUST match settings.embedding_model_revision: the app loads the
# model by revision, so baking a different snapshot would make the container try to
# download at runtime — which fails on an offline/firewalled host.
ARG EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
ARG EMBEDDING_MODEL_REVISION=5c38ec7c405ec4b44b94cc5a9bb96e735b38267a
RUN python -m spacy download en_core_web_sm \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL}', revision='${EMBEDDING_MODEL_REVISION}')"

# Runtime must use only the baked snapshots. Without these flags the Hugging Face
# client still performs network resolution and an offline container can hang during
# startup even though the weights are present locally.
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1

# --- Package source (editable) -----------------------------------------------
# Copied only after the model layer so normal code edits rebuild in seconds.
# Editable keeps the package at /app/src, so path resolution for kb/, widget/ and
# dashboard/ points at /app. `--no-deps` prevents redundant dependency resolution.
COPY src ./src
RUN pip install --no-deps -e .

# --- App content the API serves and ingests from -----------------------------
# Copied last (changes more often than code/deps) for better layer caching.
COPY kb ./kb
COPY widget ./widget
COPY dashboard ./dashboard

# --- Run as a non-root user --------------------------------------------------
# App code and baked models are runtime read-only and world-readable. Do not
# recursively chown them: touching the multi-GB model tree made every tiny widget
# or KB edit export a huge new layer.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Readiness probe using only the stdlib (no curl in the image).
HEALTHCHECK --interval=30s --timeout=5s --start-period=240s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/ready').status==200 else 1)"

CMD ["uvicorn", "msfea_bot.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

# --- Persistent development/test image --------------------------------------
# Built explicitly through docker-compose.dev.yml. It inherits the exact runtime
# environment and baked models used in production, then adds the pinned tools once
# so every lint/type/test run does not download them into a disposable container.
FROM production AS development

USER root
RUN pip install -e ".[dev,gemini]"
USER appuser

WORKDIR /workspace
HEALTHCHECK NONE
CMD ["python", "-m", "pytest", "-q"]

# Keep a plain `docker build .` production-safe even though the development stage
# must be declared after it in order to inherit the complete runtime image.
FROM production AS final
