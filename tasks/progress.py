"""
Redis-Based Progress Tracker
M-Code Pro - Celery Background Task Processing

Replaces in-memory progress tracker with Redis for multi-worker support.
Progress survives worker restarts and is shared across all workers.
"""

import redis
import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Redis connection
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(REDIS_URL + '/2', decode_responses=True)  # DB 2 for progress


class RedisProgressTracker:
    """Redis-based progress tracker for multi-worker Celery setup"""
    
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 86400  # 24 hours
    
    def _key(self, job_id: str) -> str:
        """Generate Redis key for job"""
        return f"progress:{job_id}"
    
    def set_progress(self, job_id: str, progress_data: Dict[str, Any], ttl: Optional[int] = None):
        """
        Set progress data for a job
        
        Args:
            job_id: Classification job ID
            progress_data: Dict with progress information
            ttl: Time-to-live in seconds (default: 24 hours)
        """
        key = self._key(job_id)
        ttl = ttl or self.default_ttl
        
        # Serialize and store
        self.redis.setex(
            key,
            ttl,
            json.dumps(progress_data, default=str)
        )
    
    def get_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress data for a job
        
        Args:
            job_id: Classification job ID
            
        Returns:
            Progress data dict or None if not found
        """
        key = self._key(job_id)
        data = self.redis.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    def update_progress(self, job_id: str, **updates):
        """
        Update specific fields in progress data
        
        Args:
            job_id: Classification job ID
            **updates: Key-value pairs to update
        """
        current = self.get_progress(job_id) or {}
        current.update(updates)
        self.set_progress(job_id, current)
    
    def delete_progress(self, job_id: str):
        """
        Delete progress data for a job
        
        Args:
            job_id: Classification job ID
        """
        key = self._key(job_id)
        self.redis.delete(key)
    
    def get_all_jobs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get progress data for all jobs
        
        Returns:
            Dict mapping job_id to progress data
        """
        pattern = self._key("*")
        keys = self.redis.keys(pattern)
        
        result = {}
        for key in keys:
            job_id = key.split(":", 1)[1]  # Extract job_id from "progress:job_id"
            data = self.redis.get(key)
            if data:
                result[job_id] = json.loads(data)
        
        return result
    
    def set_variable_progress(self, job_id: str, variable_name: str, progress_data: Dict[str, Any]):
        """
        Set progress for a specific variable within a job
        
        Args:
            job_id: Classification job ID
            variable_name: Variable being classified
            progress_data: Progress data for this variable
        """
        job_progress = self.get_progress(job_id) or {}
        
        if 'variables' not in job_progress:
            job_progress['variables'] = {}
        
        job_progress['variables'][variable_name] = progress_data
        self.set_progress(job_id, job_progress)
    
    def get_variable_progress(self, job_id: str, variable_name: str) -> Optional[Dict[str, Any]]:
        """
        Get progress for a specific variable
        
        Args:
            job_id: Classification job ID
            variable_name: Variable name
            
        Returns:
            Variable progress data or None
        """
        job_progress = self.get_progress(job_id)
        if job_progress and 'variables' in job_progress:
            return job_progress['variables'].get(variable_name)
        return None


# Global progress tracker instance
progress_tracker = RedisProgressTracker()


# Convenience functions for backward compatibility
def set_progress(job_id: str, progress_data: Dict[str, Any]):
    """Set progress data (backward compatible)"""
    progress_tracker.set_progress(job_id, progress_data)


def get_progress(job_id: str) -> Optional[Dict[str, Any]]:
    """Get progress data (backward compatible)"""
    return progress_tracker.get_progress(job_id)


def update_progress(job_id: str, **updates):
    """Update progress data (backward compatible)"""
    progress_tracker.update_progress(job_id, **updates)


def delete_progress(job_id: str):
    """Delete progress data (backward compatible)"""
    progress_tracker.delete_progress(job_id)


__all__ = [
    'RedisProgressTracker',
    'progress_tracker',
    'set_progress',
    'get_progress',
    'update_progress',
    'delete_progress'
]
