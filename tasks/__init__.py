"""
Tasks Package
M-Code Pro - Celery Background Tasks

This package contains all Celery task definitions:
- classification.py: Classification tasks
- progress.py: Progress tracking with Redis
"""

from celery_app import celery_app

__all__ = ['celery_app']
