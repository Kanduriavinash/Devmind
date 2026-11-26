FROM node:22-bookworm-slim

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN printf 'devmind:x:10001:10001:DevMind sandbox:/tmp:/bin/sh\n' >> /etc/passwd \
    && printf 'devmind:x:10001:\n' >> /etc/group

WORKDIR /workspace
USER 10001:10001
