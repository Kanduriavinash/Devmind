FROM python:3.12-slim-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN printf 'devmind:x:10001:10001:DevMind sandbox:/tmp:/bin/sh\n' >> /etc/passwd \
    && printf 'devmind:x:10001:\n' >> /etc/group

RUN python -m pip install --no-cache-dir pytest==8.3.5

WORKDIR /workspace
USER 10001:10001
