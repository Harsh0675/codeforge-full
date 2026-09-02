#!/usr/bin/env bash
set -e
docker build -t codeforge-runner-python runner-images/python
docker build -t codeforge-runner-cpp runner-images/cpp
docker build -t codeforge-runner-node runner-images/node
docker build -t codeforge-runner-java runner-images/java
docker build -t codeforge-runner-go runner-images/go
docker build -t codeforge-runner-rust runner-images/rust
docker build -t codeforge-runner-php runner-images/php
docker compose up --build
