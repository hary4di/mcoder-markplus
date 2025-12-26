#!/bin/bash
# Auto-cleanup script for M-Coder classified files
# Deletes files older than 24 hours from uploads directory

LOG_FILE="/var/log/mcoder/cleanup.log"
UPLOADS_DIR="/opt/markplus/mcoder-markplus/files/uploads"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting cleanup..." >> "$LOG_FILE"

# Find and delete Excel files older than 24 hours
FILES_DELETED=$(find "$UPLOADS_DIR" -name "*.xlsx" -type f -mtime +1 -print -delete 2>> "$LOG_FILE" | wc -l)

if [ "$FILES_DELETED" -gt 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $FILES_DELETED file(s)" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - No files to clean up" >> "$LOG_FILE"
fi

# Keep only last 100 lines of log
tail -100 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"

echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup complete" >> "$LOG_FILE"
