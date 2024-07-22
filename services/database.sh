#!/bin/bash

# Function to check if the MySQL service is running
check_mysql() {
    systemctl is-active --quiet mysql
    return $?
}

# Start the MySQL service
start_mysql() {
    echo "Starting MySQL service..."
    sudo systemctl start mysql
}

# Enable MySQL service to start on boot
enable_mysql() {
    echo "Enabling MySQL service to start on boot..."
    sudo systemctl enable mysql
}

# Main script execution
echo "Checking MySQL service status..."
if check_mysql; then
    echo "MySQL service is already running."
else
    start_mysql
    if check_mysql; then
        echo "MySQL service started successfully."
    else
        echo "Failed to start MySQL service."
        exit 1
    fi
fi

enable_mysql
echo "Script execution completed."