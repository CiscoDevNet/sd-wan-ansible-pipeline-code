# Use an official Python runtime as a parent image
FROM python:3

# Install OS requirements
RUN apt-get update && apt-get install -y python-pip openssh-client curl sshpass

# Install Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --requirement /tmp/requirements.txt
RUN pip install virlutils

# Setup environment
ENV ANSIBLE_HOST_KEY_CHECKING false
ENV ANSIBLE_RETRY_FILES_ENABLED false
ENV ANSIBLE_SSH_PIPELINING True

# Define working directory
WORKDIR /ansible