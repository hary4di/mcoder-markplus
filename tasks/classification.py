"""
Classification Celery Task
M-Code Pro - Background Classification Processing

This module contains the main Celery task for classification:
- Runs classification in background worker
- Tasks survive browser close/logout
- Progress tracked in Redis
- Multiple concurrent classifications supported
"""

from celery_app import celery_app
from tasks.progress import progress_tracker
import os
import json
from datetime import datetime
import time


@celery_app.task(bind=True, name='tasks.classification.classify_dataset')
def classify_dataset(self, job_id, kobo_system_path, raw_data_path, variables_to_process,
                     max_categories, confidence_threshold, auto_upload, classification_mode,
                     user_id, kobo_original_filename, raw_original_filename):
    """
    Celery task to run classification in background
    
    Args:
        self: Celery task instance (bind=True)
        job_id: Unique job identifier
        kobo_system_path: Path to kobo system file
        raw_data_path: Path to raw data file
        variables_to_process: List of variables to classify
        max_categories: Maximum categories per variable
        confidence_threshold: Minimum confidence score
        auto_upload: Whether to upload to Kobo
        classification_mode: 'pure' or 'semi'
        user_id: User ID who submitted the job
        kobo_original_filename: Original kobo filename
        raw_original_filename: Original raw filename
        
    Returns:
        dict: Classification results
    """
    import sys
    import traceback
    
    # Import Flask app and models
    from app import create_app, db
    from app.models import ClassificationJob, ClassificationVariable
    from excel_classifier import ExcelClassifier
    
    print(f"\n{'='*80}")
    print(f"[CELERY TASK] Classification task started")
    print(f"[CELERY TASK] Task ID: {self.request.id}")
    print(f"[CELERY TASK] Job ID: {job_id}")
    print(f"[CELERY TASK] Variables to process: {len(variables_to_process)}")
    print(f"{'='*80}\n", flush=True)
    
    try:
        # Initialize progress in Redis
        progress_tracker.set_progress(job_id, {
            'status': 'processing',
            'progress': 0,
            'current_step': 'Initializing...',
            'started_at': datetime.utcnow().isoformat(),
            'task_id': self.request.id,
            'variables': {},
            'total_variables': len(variables_to_process)
        })
        
        # Small delay to ensure data is synced
        time.sleep(0.5)
        
        # Create Flask app context for database operations
        app = create_app()
        with app.app_context():
            # Generate output filenames with timestamp in files/output/ directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Get base directory (files/) and create output directory
            files_dir = os.path.dirname(os.path.dirname(raw_data_path))  # Go up from uploads/ to files/
            output_dir = os.path.join(files_dir, 'output')
            os.makedirs(output_dir, exist_ok=True)  # Create if not exists
            
            output_kobo = os.path.join(output_dir, f'output_kobo_{timestamp}.xlsx')
            output_raw = os.path.join(output_dir, f'output_raw_{timestamp}.xlsx')
            
            print(f"[CELERY TASK] Output directory: {output_dir}", flush=True)
            
            # Create job record in database
            classification_job = ClassificationJob(
                job_id=job_id,
                task_id=self.request.id,  # Store Celery task ID
                user_id=user_id,
                job_type='open_ended',
                status='processing',
                original_kobo_filename=kobo_original_filename,
                original_raw_filename=raw_original_filename,
                input_kobo_path=kobo_system_path,
                input_raw_path=raw_data_path,
                output_kobo_filename=os.path.basename(output_kobo),
                output_raw_filename=os.path.basename(output_raw),
                output_kobo_path=output_kobo,
                output_raw_path=output_raw,
                settings=json.dumps({
                    'max_categories': max_categories,
                    'confidence_threshold': confidence_threshold,
                    'auto_upload': auto_upload,
                    'classification_mode': classification_mode
                }),
                started_at=datetime.utcnow()
            )
            db.session.add(classification_job)
            db.session.commit()
            print(f"[CELERY TASK] ClassificationJob created in database (ID: {classification_job.id})", flush=True)
        
        # Initialize classifier
        print(f"[CELERY TASK] Initializing ExcelClassifier...", flush=True)
        print(f"[CELERY TASK] Kobo system: {kobo_system_path}", flush=True)
        print(f"[CELERY TASK] Raw data: {raw_data_path}", flush=True)
        
        classifier = ExcelClassifier(kobo_system_path, raw_data_path)
        
        # Set output paths (preserve originals)
        classifier.set_output_paths(output_kobo, output_raw)
        print(f"[CELERY TASK] Output paths configured:", flush=True)
        print(f"[CELERY TASK]   Kobo: {output_kobo}", flush=True)
        print(f"[CELERY TASK]   Raw: {output_raw}", flush=True)
        
        print(f"[CELERY TASK] Classifier initialized successfully", flush=True)
        
        # Process each variable
        all_summaries = []
        start_time = datetime.now()
        total_vars = len(variables_to_process)
        
        for idx, var_info in enumerate(variables_to_process, 1):
            var_name = var_info['name']
            question_text = var_info['question']
            
            print(f"[CELERY TASK] Processing variable {idx}/{total_vars}: {var_name}", flush=True)
            
            # Update progress in Redis - starting variable
            progress_tracker.set_variable_progress(job_id, var_name, {
                'status': 'processing',
                'progress': 0,
                'step': 'Starting...',
                'index': idx,
                'total': total_vars,
                'question': question_text
            })
            
            # Update overall progress
            overall_progress = int(((idx - 1) / total_vars) * 100)
            progress_tracker.update_progress(
                job_id,
                progress=overall_progress,
                current_step=f'Processing variable {idx}/{total_vars}: {var_name}'
            )
            
            # Update Celery task progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': overall_progress,
                    'current': idx,
                    'total': total_vars,
                    'variable': var_name
                }
            )
            
            # Create progress callback for classifier
            def update_classifier_progress(message, percentage):
                """Callback function to update progress from classifier"""
                print(f"[CALLBACK] {var_name}: {message} ({percentage}%)", flush=True)
                
                # Update variable progress in Redis
                progress_tracker.set_variable_progress(job_id, var_name, {
                    'status': 'processing',
                    'progress': percentage,
                    'step': message,
                    'index': idx,
                    'total': total_vars,
                    'question': question_text
                })
                
                # Update overall job progress
                var_progress = ((idx - 1) / total_vars) + (percentage / 100 / total_vars)
                overall_progress = int(var_progress * 100)
                progress_tracker.update_progress(
                    job_id,
                    progress=overall_progress,
                    current_step=f'[{var_name}] {message}'
                )
            
            # Process variable with progress callback
            print(f"[CELERY TASK] Calling classifier.process_variable for {var_name}...", flush=True)
            print(f"[CELERY TASK] Classification mode: {classification_mode}", flush=True)
            
            try:
                summary = classifier.process_variable(
                    var_name,
                    question_text,
                    progress_callback=update_classifier_progress,
                    classification_mode=classification_mode
                )
                print(f"[CELERY TASK] Variable {var_name} processed successfully", flush=True)
            except Exception as var_error:
                print(f"[CELERY TASK ERROR] Failed to process variable {var_name}: {str(var_error)}", flush=True)
                traceback.print_exc()
                raise
            
            # Save variable results to database
            with app.app_context():
                # Query job again to avoid detached instance error
                job_to_update = ClassificationJob.query.filter_by(job_id=job_id).first()
                if not job_to_update:
                    print(f"[CELERY TASK ERROR] Job {job_id} not found!", flush=True)
                    continue
                
                classification_var = ClassificationVariable(
                    job_id=job_to_update.id,
                    variable_name=var_name,
                    question_text=question_text,
                    categories_generated=summary.get('categories_generated', 0),
                    total_responses=summary.get('total_responses', 0),
                    valid_classified=summary.get('valid_classified', 0),
                    invalid_count=summary.get('invalid_count', 0),
                    empty_count=summary.get('empty_count', 0),
                    categories=json.dumps(summary.get('category_summary', [])),
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    status='completed'
                )
                db.session.add(classification_var)
                
                # Update job progress in database
                job_to_update.progress = int((idx / total_vars) * 100)
                job_to_update.current_step = f"Completed {idx}/{total_vars} variables"
                db.session.commit()
                print(f"[CELERY TASK] Saved variable {var_name} to database", flush=True)
            
            # Mark variable as complete in Redis
            progress_tracker.set_variable_progress(job_id, var_name, {
                'status': 'completed',
                'progress': 100,
                'step': 'Completed',
                'index': idx,
                'total': total_vars,
                'question': question_text,
                'summary': summary
            })
            
            all_summaries.append(summary)
            print(f"[CELERY TASK] Progress: {idx}/{total_vars} variables completed", flush=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Prepare results
        results = {
            'summaries': all_summaries,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': duration,
            'total_variables': total_vars,
            'settings': {
                'max_categories': max_categories,
                'confidence_threshold': confidence_threshold,
                'auto_upload': auto_upload
            },
            'output_files': {
                'kobo': os.path.basename(output_kobo),
                'raw': os.path.basename(output_raw)
            }
        }
        
        # Update job as completed in database
        with app.app_context():
            # Query job again in this context
            job_to_update = ClassificationJob.query.filter_by(job_id=job_id).first()
            if job_to_update:
                job_to_update.status = 'completed'
                job_to_update.completed_at = datetime.utcnow()
                job_to_update.progress = 100
                job_to_update.results_summary = json.dumps(results)
                db.session.commit()
                print(f"[CELERY TASK] Updated ClassificationJob status to completed", flush=True)
            else:
                print(f"[CELERY TASK ERROR] Job {job_id} not found for completion update!", flush=True)
        
        # Delete input files to save disk space (keep only output files)
        try:
            if os.path.exists(kobo_system_path):
                os.remove(kobo_system_path)
                print(f"[CELERY TASK] Deleted input file: {os.path.basename(kobo_system_path)}", flush=True)
            
            if os.path.exists(raw_data_path):
                os.remove(raw_data_path)
                print(f"[CELERY TASK] Deleted input file: {os.path.basename(raw_data_path)}", flush=True)
            
            print(f"[CELERY TASK] Input files deleted successfully (only output files remain)", flush=True)
        except Exception as delete_error:
            # Log error but don't fail the job
            print(f"[CELERY TASK WARNING] Failed to delete input files: {str(delete_error)}", flush=True)
        
        # Mark job as complete in Redis
        progress_tracker.update_progress(
            job_id,
            status='completed',
            progress=100,
            current_step='Classification completed',
            completed_at=datetime.utcnow().isoformat(),
            results=results
        )
        
        print(f"[CELERY TASK] Classification job {job_id} completed successfully", flush=True)
        
        return results
        
    except Exception as e:
        error_msg = str(e)
        print(f"[CELERY TASK ERROR] Classification failed: {error_msg}", flush=True)
        traceback.print_exc()
        
        # Update job as failed in database
        try:
            with app.app_context():
                # Query job again in this context
                job_to_update = ClassificationJob.query.filter_by(job_id=job_id).first()
                if job_to_update:
                    job_to_update.status = 'error'
                    job_to_update.error_message = error_msg
                    job_to_update.completed_at = datetime.utcnow()
                    db.session.commit()
                    print(f"[CELERY TASK] Updated ClassificationJob status to error", flush=True)
                else:
                    print(f"[CELERY TASK ERROR] Job {job_id} not found for error update!", flush=True)
        except Exception as db_error:
            print(f"[CELERY TASK] Failed to update database: {db_error}", flush=True)
        
        # Update progress in Redis
        progress_tracker.update_progress(
            job_id,
            status='error',
            error_message=error_msg,
            completed_at=datetime.utcnow().isoformat()
        )
        
        # Propagate exception to Celery
        raise


__all__ = ['classify_dataset']
