"""
Database Migration: Add task_id column to classification_jobs table
M-Code Pro - Phase 1: Redis + Celery Implementation

This script adds task_id column to track Celery task IDs.
Run with: python add_task_id_column.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import ClassificationJob
from sqlalchemy import text

def add_task_id_column():
    """Add task_id column to classification_jobs table"""
    
    app = create_app()
    
    with app.app_context():
        print("="*80)
        print("Database Migration: Add task_id Column")
        print("="*80)
        
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('classification_jobs')]
            
            if 'task_id' in columns:
                print("✓ Column 'task_id' already exists. Skipping migration.")
                return
            
            print("Adding 'task_id' column to classification_jobs table...")
            
            # PostgreSQL syntax
            if 'postgresql' in str(db.engine.url):
                db.session.execute(text(
                    "ALTER TABLE classification_jobs ADD COLUMN task_id VARCHAR(36)"
                ))
                db.session.execute(text(
                    "CREATE INDEX IF NOT EXISTS ix_classification_jobs_task_id ON classification_jobs(task_id)"
                ))
            # SQLite syntax
            else:
                db.session.execute(text(
                    "ALTER TABLE classification_jobs ADD COLUMN task_id VARCHAR(36)"
                ))
                # SQLite doesn't support CREATE INDEX IF NOT EXISTS in older versions
                try:
                    db.session.execute(text(
                        "CREATE INDEX ix_classification_jobs_task_id ON classification_jobs(task_id)"
                    ))
                except:
                    print("Warning: Index may already exist or SQLite version doesn't support this syntax")
            
            db.session.commit()
            
            print("✓ Successfully added 'task_id' column")
            print("✓ Successfully added index on 'task_id'")
            print("\nMigration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_task_id_column()
