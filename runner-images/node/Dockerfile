FROM node:22-bookworm-slim
RUN npm install -g typescript@5.9.2 && \
    useradd -u 10001 -m runner
USER runner
WORKDIR /workspace
CMD ["sleep","infinity"]
