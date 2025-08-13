#!/bin/bash
# Foodyeh Backup Script
# Creates daily backups of database and uploads

set -e

# Configuration
BACKUP_DIR="/opt/foodyeh/backups"
DB_PATH="/opt/foodyeh/backend/foodyeh.db"
UPLOADS_PATH="/opt/foodyeh/backend/uploads"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="foodyeh_backup_${DATE}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Create backup archive
echo "Creating backup: ${BACKUP_NAME}"

# Backup database
if [ -f "${DB_PATH}" ]; then
    echo "Backing up database..."
    cp "${DB_PATH}" "${BACKUP_DIR}/foodyeh_${DATE}.db"
    gzip "${BACKUP_DIR}/foodyeh_${DATE}.db"
fi

# Backup uploads directory
if [ -d "${UPLOADS_PATH}" ]; then
    echo "Backing up uploads..."
    tar -czf "${BACKUP_DIR}/uploads_${DATE}.tar.gz" -C "${UPLOADS_PATH}" .
fi

# Create combined backup
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" \
    "foodyeh_${DATE}.db.gz" \
    "uploads_${DATE}.tar.gz" 2>/dev/null || true

# Clean up individual files
rm -f "foodyeh_${DATE}.db.gz" "uploads_${DATE}.tar.gz"

# Keep only last 7 days of backups
find "${BACKUP_DIR}" -name "foodyeh_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Optional: Upload to remote storage (uncomment and configure)
# echo "Uploading to remote storage..."
# aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" s3://your-backup-bucket/ || true
