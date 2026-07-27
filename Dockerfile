# syntax=docker/dockerfile:1
#
# Production image for the MSFEA CDC chatbot API (CLAUDE.md §3, §5.10).
# Design goals: portable (builds on x86_64 and Apple-Silicon/arm64), offline at
# runtime (models baked in — safe behind AUB's firewall), reproducible, non-root.

FROM python:3.12-slim

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

# --- Dependencies + package (EDITABLE install) -------------------------------
# Editable keeps the package at /app/src, so the app's path resolution for kb/,
# widget/ and dashboard/ (Path(__file__).parents[3]) points at /app. A normal
# install would relocate the package into site-packages and break those paths.
# torch is already satisfied above, so this won't pull the CUDA build.
COPY src ./src
RUN pip install -e ".[gemini]"

# --- Bake models so the container needs NO internet at runtime ---------------
# Fast startup and firewall-safe. Override at build time with
# --build-arg EMBEDDING_MODEL=... if you change the default embedding model.
ARG EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
RUN python -m spacy download en_core_web_sm \
 && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL}')"

# --- App content the API serves and ingests from -----------------------------
# Copied last (changes more often than code/deps) for better layer caching.
COPY kb ./kb
COPY widget ./widget
COPY dashboard ./dashboard

# --- Run as a non-root user --------------------------------------------------
RUN useradd --create-home --uid 10001 appuser \
 && chown -R appuser:appuser /app /opt/models
USER appuser

EXPOSE 8000

# Liveness probe using only the stdlib (no curl in the image).
HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

CMD ["uvicorn", "msfea_bot.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
