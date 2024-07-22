#!/bin/bash

# Function to check if openssh-server is installed
check_sshd_installed() {
    dpkg -l | grep -qw openssh-server
    return $?
}

# Function to install openssh-server if not installed
install_sshd() {
    echo "Installing openssh-server..."
    sudo apt update
    sudo apt install -y openssh-server
}

# Function to start ssh service
start_sshd() {
    echo "Starting ssh service..."
    sudo systemctl start ssh
}

# Function to enable ssh service to start on boot
enable_sshd() {
    echo "Enabling ssh service to start on boot..."
    sudo systemctl enable ssh
}

# Main script execution
echo "Checking if openssh-server is installed..."
if check_sshd_installed; then
    echo "openssh-server is already installed."
else
    install_sshd
fi

echo "Starting and enabling ssh service..."
start_sshd
enable_sshd

echo "Script execution completed."