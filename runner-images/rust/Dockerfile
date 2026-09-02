FROM rust:1.87-bookworm
RUN useradd -u 10001 -m runner
RUN ln -s /usr/local/rustup/toolchains/1.87.0-x86_64-unknown-linux-gnu/bin/rustc /usr/local/bin/rustc
USER runner
WORKDIR /workspace
CMD ["sleep","infinity"]
