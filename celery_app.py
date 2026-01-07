"""
Celery Application Configuration
M-Code Pro - Background Task Processing

This module initializes Celery for asynchronous task processing:
- Classification tasks run in background
- Tasks survive browser close/logout
- Redis as message broker and result backend
- Multiple workers for concurrent processing
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis configuration from environment
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Initialize Celery app
celery_app = Celery(
    'mcoder',
    broker=f'{REDIS_URL}/0',  # Redis DB 0 for message queue
    backend=f'{REDIS_URL}/1'   # Redis DB 1 for result storage
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='Asia/Jakarta',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'tasks.classification.*': {'queue': 'classification'},
        'tasks.progress.*': {'queue': 'default'},
    },
    
    # Worker settings
    worker_prefetch_multiplier=2,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=86400,  # 24 hours
    result_backend_transport_options={
        'visibility_timeout': 3600,  # 1 hour
    },
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Time limits
    task_soft_time_limit=3600,  # 1 hour soft limit
    task_time_limit=3900,       # 65 minutes hard limit
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# Task discovery
celery_app.autodiscover_tasks(['tasks'])


# Celery signals for logging
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """Log when task starts"""
    print(f"Task {task.name} [{task_id}] started")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **extra):
    """Log when task completes"""
    print(f"Task {task.name} [{task_id}] completed with state: {state}")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **extra):
    """Log when task fails"""
    print(f"Task {sender.name} [{task_id}] failed: {exception}")


# Make celery app importable
__all__ = ['celery_app']
