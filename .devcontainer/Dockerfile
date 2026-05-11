FROM mcr.microsoft.com/devcontainers/python:3.12

# PlatformIO requires udev rules and the user in the dialout group for serial access
RUN apt-get update && apt-get install -y --no-install-recommends \
        udev \
        libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Add vscode user to dialout for serial port access
RUN usermod -aG dialout vscode

# Install PlatformIO CLI
RUN pip install --no-cache-dir platformio
