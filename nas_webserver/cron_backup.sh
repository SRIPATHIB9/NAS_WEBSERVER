#!/bin/bash

# Set timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Directories
BACKUP_DIR="./backups"
UPLOAD_DIR="./uploads"

# Make sure backup dir exists
mkdir -p "$BACKUP_DIR"

# Create backup zip
zip -r "$BACKUP_DIR/backup_$TIMESTAMP.zip" "$UPLOAD_DIR"

# Optional: log backup
echo "Backup created at $TIMESTAMP" >> "$BACKUP_DIR/backup.log"
