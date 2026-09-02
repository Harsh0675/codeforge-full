FROM golang:1.24-bookworm
RUN useradd -u 10001 -m runner
RUN ln -s /usr/local/go/bin/go /usr/local/bin/go
USER runner
WORKDIR /workspace
CMD ["sleep","infinity"]
