# FROM python:3.9-slim
FROM ubuntu:20.04
# Switch to root user to install packages
USER root

# Update and install dependencies using apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    python3-venv \
    python3\
    python3-distutils\
    python3-pip\
    gdb \
    binutils \
    tmux \
    sudo \
    git \
    gdb-multiarch \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the Python interpreter path for GDB
# ENV PYTHONHOME=/usr/local/lib/python3.9
# ENV PYTHONPATH=/usr/local/lib/python3.9/site-packages
# ENV LD_LIBRARY_PATH=/usr/local/lib/python3.9/lib:$LD_LIBRARY_PATH
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy all files and directories from the current context to the image
COPY . /app/

USER root
RUN chmod +x /app/*.py
RUN chmod +x /app/*.sh

# Set the default entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]


# FROM python:3.9-alpine

# # Update and install dependencies
# RUN apt-get update && apt-get install -y \
#     python3 python3-pip gdb-multiarch tmux sudo git \
#     && apt-get clean


# RUN useradd -ms /bin/bash developer
# RUN echo "developer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/developer

# USER developer
# WORKDIR /app

# # Copy all files and directories from the current context to the image
# COPY . /app/
# USER root
# RUN chmod +x /app/*.py
# USER developer

# # Install Python dependencies with sudo
# RUN sudo pip3 install -r requirements.txt

# ENTRYPOINT ["bash", "-c"]
