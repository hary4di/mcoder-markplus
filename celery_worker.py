"""
Start Celery Worker
M-Code Pro - Background Task Processing

This script starts the Celery worker for processing classification tasks.

Usage:
    python celery_worker.py

Or with more options:
    celery -A celery_app worker --loglevel=info --concurrency=4 -Q classification,default
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Celery app
from celery_app import celery_app

if __name__ == '__main__':
    # Start Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',  # 4 concurrent workers
        '-Q', 'classification,default',  # Listen to both queues
        '-n', 'worker@%h',  # Worker name
        '--logfile=/var/log/mcoder/celery.log',  # Log file
        '--pidfile=/tmp/celery-mcoder.pid',  # PID file
    ])
