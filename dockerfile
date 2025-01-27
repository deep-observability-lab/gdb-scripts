# FROM python:3.9-slim
FROM ubuntu:20.04

# Switch to root user to install packages
USER root

# Update and install dependencies using apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    python3-venv \
    python3 \
    python3-distutils \
    python3-pip \
    gdb \
    binutils \
    tmux \
    sudo \
    git \
    gdb-multiarch \
    bash \
    gcc-powerpc-linux-gnu \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy all files and directories from the current context to the image
COPY . /app/

# Set ARG and ENV variables
ARG HOST_PATH
ENV HOST_PATH=${HOST_PATH}

# Make scripts executable
RUN chmod +x /app/*.py
RUN chmod +x /app/*.sh

# Set the default entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]