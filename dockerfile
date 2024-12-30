FROM ubuntu:22.04

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip gdb gnome-terminal sudo git \
    && apt-get clean


RUN useradd -ms /bin/bash developer
RUN echo "developer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/developer

USER developer
WORKDIR /home/developer

# Copy all files and directories from the current context to the image
COPY . /home/developer/
USER root
RUN chmod +x /home/developer/*.py
USER developer

# Install Python dependencies with sudo
RUN sudo pip3 install -r requirements.txt

ENTRYPOINT ["bash", "-c"]
CMD ["echo 'Run one of the scripts with the desired arguments, e.g., gdb_remote.py or gdb_coredump.py.'"]
