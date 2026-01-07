"""
Main Application Routes
"""
import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session, Response, stream_with_context, send_file, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import User, SystemSettings
from app.forms import ClassificationForm
from app.utils import FileProcessor
# Use Redis-based progress tracker instead of in-memory
from tasks.progress import progress_tracker
# Import Celery task for background processing
from tasks.classification import classify_dataset
from config import Config
from excel_classifier import ExcelClassifier

main_bp = Blueprint('main', __name__)

# Initialize file processor
file_processor = FileProcessor(Config.UPLOAD_FOLDER)

@main_bp.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    logo_filename = SystemSettings.get_setting('logo_filename', None) if SystemSettings else None
    logo_url = url_for('main.serve_logo', filename=logo_filename) if logo_filename else None
    return dict(now=datetime.now(), logo_url=logo_url)

@main_bp.before_request
def log_request():
    """Log all incoming requests for debugging"""
    print(f"\n[REQUEST] {request.method} {request.path}", flush=True)
    print(f"[REQUEST] Remote addr: {request.remote_addr}", flush=True)
    if request.form:
        print(f"[REQUEST] Form data keys: {list(request.form.keys())}", flush=True)
    print(f"", flush=True)

@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@main_bp.route('/responsive-test')
def responsive_test():
    """Responsive design test page"""
    return render_template('responsive_test.html')

@main_bp.route('/classify', methods=['GET', 'POST'])
@login_required
def classify():
    """Classification page - Step 1: File Upload"""
    return render_template('classify.html')

@main_bp.route('/upload-files', methods=['POST'])
@login_required
def upload_files():
    """Handle file upload"""
    try:
        # Check if files were uploaded
        if 'kobo_system_file' not in request.files:
            return jsonify({'success': False, 'error': 'Kobo system file is required'}), 400
        
        if 'raw_data_file' not in request.files:
            return jsonify({'success': False, 'error': 'Raw data file is required'}), 400
        
        kobo_file = request.files['kobo_system_file']
        raw_file = request.files['raw_data_file']
        
        if kobo_file.filename == '' or raw_file.filename == '':
            return jsonify({'success': False, 'error': 'Both files must be selected'}), 400
        
        # Validate file extensions
        if not file_processor.allowed_file(kobo_file.filename):
            return jsonify({'success': False, 'error': 'Invalid kobo system file format'}), 400
        
        if not file_processor.allowed_file(raw_file.filename):
            return jsonify({'success': False, 'error': 'Invalid raw data file format'}), 400
        
        # Save files with original names (no timestamp)
        kobo_path, kobo_original = file_processor.save_file(kobo_file, prefix='', add_timestamp=False)
        raw_path, raw_original = file_processor.save_file(raw_file, prefix='', add_timestamp=False)
        
        # Validate structure
        is_valid, error_msg = file_processor.validate_excel_structure(raw_path)
        if not is_valid:
            os.remove(kobo_path)
            os.remove(raw_path)
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Get file info
        file_info = file_processor.get_file_info(raw_path)
        
        # Detect variables from kobo_system
        detected_vars = file_processor.detect_open_ended_variables(kobo_path)
        
        # Detect semi open-ended pairs
        semi_open_pairs = file_processor.detect_semi_open_pairs(kobo_path)
        
        if not detected_vars and not semi_open_pairs:
            os.remove(kobo_path)
            os.remove(raw_path)
            return jsonify({'success': False, 'error': 'No open-ended or semi open-ended variables detected. Please check kobo_system file structure.'}), 400
        
        # Get statistics for each pure open-ended variable
        for var in detected_vars:
            stats = file_processor.get_variable_statistics(raw_path, var['name'])
            var.update(stats)
        
        # Get statistics for each semi open-ended pair
        for pair in semi_open_pairs:
            stats = file_processor.get_semi_open_statistics(raw_path, pair)
            pair.update(stats)
        
        # Store in session
        session['raw_data_path'] = raw_path
        session['kobo_system_path'] = kobo_path
        session['kobo_original_filename'] = kobo_original
        session['raw_original_filename'] = raw_original
        session['file_info'] = file_info
        session['detected_variables'] = detected_vars
        session['semi_open_pairs'] = semi_open_pairs
        
        return jsonify({
            'success': True,
            'message': f'Files uploaded successfully. Detected {len(detected_vars)} open-ended and {len(semi_open_pairs)} semi open-ended variables.',
            'file_info': file_info,
            'detected_variables': detected_vars,
            'semi_open_pairs': semi_open_pairs
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/select-variables')
@login_required
def select_variables():
    """Step 2: Select variables to classify"""
    detected_vars = session.get('detected_variables', [])
    semi_open_pairs = session.get('semi_open_pairs', [])
    file_info = session.get('file_info', {})
    
    if not detected_vars and not semi_open_pairs:
        flash('Please upload files first', 'warning')
        return redirect(url_for('main.classify'))
    
    return render_template('select_variables.html', 
                         variables=detected_vars,
                         semi_open_pairs=semi_open_pairs,
                         file_info=file_info)

@main_bp.route('/start-classification', methods=['POST'])
@login_required
def start_classification():
    """Step 3: Start classification process in background"""
    print(f"\n{'='*80}", flush=True)
    print(f"[ROUTE] start_classification called", flush=True)
    print(f"[ROUTE] Request method: {request.method}", flush=True)
    print(f"[ROUTE] Form data: {request.form}", flush=True)
    print(f"{'='*80}\n", flush=True)
    
    try:
        # Get data from session
        raw_data_path = session.get('raw_data_path')
        kobo_system_path = session.get('kobo_system_path')
        detected_vars = session.get('detected_variables', [])
        semi_open_pairs = session.get('semi_open_pairs', [])
        
        if not raw_data_path or not kobo_system_path:
            flash('Files not found. Please upload again.', 'error')
            return redirect(url_for('main.classify'))
        
        # Check what type of classification is being requested
        selected_var_names = request.form.getlist('selected_vars')  # Pure open-ended
        selected_semi_open = request.form.getlist('selected_semi_open')  # Semi open-ended
        
        if not selected_var_names and not selected_semi_open:
            flash('Please select at least 1 variable or pair to process', 'warning')
            return redirect(url_for('main.select_variables'))
        
        # Determine processing type
        if selected_semi_open:
            # Semi open-ended processing
            processing_type = 'semi_open'
            
            # Get semi open-ended settings
            semi_open_max_categories = int(request.form.get('semi_open_max_categories', 10))
            create_merged_column = request.form.get('create_merged_column') == 'on'
            
            # Build pairs list
            pairs_to_process = []
            for select_var in selected_semi_open:
                # Find the pair in session data
                pair = next((p for p in semi_open_pairs if p['select_var'] == select_var), None)
                if pair:
                    pairs_to_process.append(pair)
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            session['classification_job_id'] = job_id
            
            print(f"\n{'='*80}")
            print(f"[MAIN] Starting SEMI OPEN-ENDED job: {job_id}")
            print(f"[MAIN] Pairs to process: {len(pairs_to_process)}")
            print(f"[MAIN] Max categories: {semi_open_max_categories}")
            print(f"[MAIN] NOTE: Semi open-ended still uses threading (Celery migration pending)")
            print(f"{'='*80}\n")
            
            # Initialize progress tracker
            # TODO: Migrate semi open-ended to Celery task (Phase 1.5)
            import threading
            from app.progress_tracker import progress_tracker as memory_tracker
            memory_tracker.create_job(job_id, len(pairs_to_process))
            
            # Start semi open-ended processing
            thread = threading.Thread(
                target=run_semi_open_background,
                args=(job_id, kobo_system_path, raw_data_path, pairs_to_process, 
                      semi_open_max_categories, create_merged_column)
            )
            thread.daemon = True
            thread.start()
            
        else:
            # Pure open-ended processing (existing logic)
            processing_type = 'open_ended'
            
            # Get settings
            max_categories = int(request.form.get('max_categories', 10))
            confidence_threshold = float(request.form.get('confidence_threshold', 0.50))
            auto_upload = request.form.get('auto_upload') == 'on'
            classification_mode = request.form.get('classification_mode', 'incremental')
            
            # Build variable list with question context
            variables_to_process = []
            for var_name in selected_var_names:
                question_context = request.form.get(f'question_{var_name}', '')
                variables_to_process.append({
                    'name': var_name,
                    'question': question_context
                })
            
            # Generate job ID
            job_id = str(uuid.uuid4())
            session['classification_job_id'] = job_id
            
            print(f"\n{'='*80}")
            print(f"[MAIN] Starting PURE OPEN-ENDED job: {job_id}")
            print(f"[MAIN] Variables to process: {len(variables_to_process)}")
            print(f"[MAIN] Classification mode: {classification_mode}")
            print(f"{'='*80}\n")
            
            # Initialize progress tracker in Redis
            progress_tracker.set_progress(job_id, {
                'status': 'pending',
                'progress': 0,
                'current_step': 'Initializing...',
                'total_variables': len(variables_to_process),
                'variables': {}
            })
            
            # Get data that needs request context (before submitting task)
            user_id = current_user.id
            kobo_original = session.get('kobo_original_filename', os.path.basename(kobo_system_path))
            raw_original = session.get('raw_original_filename', os.path.basename(raw_data_path))
            
            # Submit classification task to Celery (runs in background worker)
            task = classify_dataset.apply_async(
                args=(job_id, kobo_system_path, raw_data_path, variables_to_process,
                      max_categories, confidence_threshold, auto_upload, classification_mode,
                      user_id, kobo_original, raw_original),
                queue='classification'  # Use dedicated classification queue
            )
            
            print(f"[MAIN] Celery task submitted: {task.id}")
            print(f"[MAIN] Task state: {task.state}")
        
        # Redirect to progress page
        return redirect(url_for('main.classification_progress'))
        
    except Exception as e:
        print(f"Error starting classification: {str(e)}")
        flash(f'Error starting classification: {str(e)}', 'error')
        return redirect(url_for('main.select_variables'))

# Legacy threading-based function removed - replaced by Celery task in tasks/classification.py
# See tasks.classification.classify_dataset for current implementation

def run_semi_open_background(job_id, kobo_system_path, raw_data_path, pairs_to_process, 
                              max_categories, create_merged_column):
    """Background function to run semi open-ended processing"""
    import time
    from semi_open_processor import SemiOpenProcessor
    
    try:
        print(f"\n[SEMI_OPEN] Starting semi open-ended job: {job_id}", flush=True)
        print(f"[SEMI_OPEN] Processing {len(pairs_to_process)} pairs", flush=True)
        
        time.sleep(0.5)
        
        # Get OpenAI API key
        from app.models import SystemSettings
        api_key = SystemSettings.get_setting('openai_api_key', os.getenv('OPENAI_API_KEY', ''))
        
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError("OpenAI API key not configured. Please set it in Admin Settings.")
        
        # Initialize processor
        print(f"[SEMI_OPEN] Initializing SemiOpenProcessor...", flush=True)
        processor = SemiOpenProcessor(kobo_system_path, raw_data_path, api_key)
        processor.load_data()
        print(f"[SEMI_OPEN] Processor initialized successfully", flush=True)
        
        # Process each pair
        all_results = []
        start_time = datetime.now()
        total_pairs = len(pairs_to_process)
        
        for idx, pair in enumerate(pairs_to_process, 1):
            select_var = pair['select_var']
            text_var = pair['text_var']
            
            print(f"[SEMI_OPEN] Processing pair {idx}/{total_pairs}: {select_var} + {text_var}", flush=True)
            
            # Update progress
            progress_tracker.update_variable(job_id, f"{select_var} (semi open)", idx, total_pairs, 
                                            f"Processing {select_var} with {text_var}")
            
            # Create progress callback
            def update_progress(message, percentage):
                print(f"[SEMI_OPEN CALLBACK] {message} ({percentage}%)", flush=True)
                progress_tracker.update_step(job_id, f'[{select_var}] {message}', percentage)
            
            # Process the pair
            update_progress("Extracting 'Lainnya' responses", 10)
            result = processor.process_semi_open_pair(pair, max_categories=max_categories)
            
            if 'error' in result:
                print(f"[SEMI_OPEN] Error processing {select_var}: {result['error']}", flush=True)
                progress_tracker.complete_variable(job_id, select_var, {
                    'variable': select_var,
                    'status': 'error',
                    'error': result['error']
                })
                continue
            
            update_progress("Classification complete", 90)
            
            # Save results (update raw_data file in place)
            output_path = raw_data_path  # Overwrite existing file
            processor.save_results(result, output_path)
            
            update_progress("Results saved", 100)
            
            # Prepare summary
            summary = {
                'variable': select_var,
                'text_variable': text_var,
                'type': 'semi_open_ended',
                'lainnya_code': pair['lainnya_code'],
                'lainnya_responses': result['lainnya_count'],
                'new_categories_generated': len(result['new_categories']),
                'merged_column': result['merged_column_name'],
                'pre_coded_categories': len(result['pre_coded_labels']),
                'total_categories': len(result['pre_coded_labels']) + len(result['new_categories']),
                'status': 'success'
            }
            
            progress_tracker.complete_variable(job_id, select_var, summary)
            all_results.append(summary)
            
            print(f"[SEMI_OPEN] Pair {select_var} processed successfully", flush=True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Prepare final results
        results = {
            'summaries': all_results,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': duration,
            'total_pairs': total_pairs,
            'processing_type': 'semi_open_ended',
            'settings': {
                'max_categories': max_categories,
                'create_merged_column': create_merged_column
            }
        }
        
        # Mark job as complete
        progress_tracker.complete_job(job_id, results)
        
        print(f"[SEMI_OPEN] Job {job_id} completed successfully", flush=True)
        
    except Exception as e:
        error_msg = str(e)
        print(f"[SEMI_OPEN ERROR] Processing failed: {error_msg}", flush=True)
        import traceback
        traceback.print_exc()
        progress_tracker.set_error(job_id, error_msg)

@main_bp.route('/classification-progress')
@login_required
def classification_progress():
    """Progress monitoring page"""
    job_id = session.get('classification_job_id')
    if not job_id:
        flash('No classification process running', 'warning')
        return redirect(url_for('main.classify'))
    
    # Note: Don't check job existence here immediately after creation
    # The background thread needs a moment to initialize
    # The frontend will handle 404 errors gracefully and redirect if needed
    
    return render_template('classification_progress.html', job_id=job_id)

@main_bp.route('/api/progress/<job_id>')
@login_required
def api_progress(job_id):
    """AJAX polling endpoint - return progress as JSON"""
    try:
        progress_data = progress_tracker.get_progress(job_id)
        
        if not progress_data:
            print(f"[API_PROGRESS] Job not found: {job_id}")
            return jsonify({
                'error': 'Job not found',
                'completed': True
            }), 404
        
        print(f"[API_PROGRESS] Returning progress for {job_id}: {progress_data.get('progress', 0)}%")
        response = jsonify(progress_data)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"[API_PROGRESS] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'completed': True
        }), 500

@main_bp.route('/classification-complete/<job_id>')
@login_required
def classification_complete(job_id):
    """Endpoint to retrieve completed classification results"""
    progress_data = progress_tracker.get_progress(job_id)
    
    if not progress_data or not progress_data.get('completed'):
        flash('Classification not complete yet', 'warning')
        return redirect(url_for('main.classification_progress'))
    
    if 'results' in progress_data:
        session['classification_results'] = progress_data['results']
        flash(f'Classification complete! {progress_data["results"]["total_variables"]} variables successfully processed.', 'success')
    
    # Cleanup job data
    progress_tracker.cleanup_job(job_id)
    
    return redirect(url_for('main.results'))

@main_bp.route('/results')
@login_required
def results():
    """Results page - show classification job history"""
    from app.models import ClassificationJob
    from sqlalchemy import desc
    
    try:
        # Get all completed jobs for current user (most recent first)
        jobs = ClassificationJob.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).order_by(desc(ClassificationJob.completed_at)).limit(20).all()
        
        # Pass objects directly to template (need for properties like is_download_available)
        return render_template('results.html', jobs=jobs)
        
    except Exception as e:
        print(f"[ERROR] Results page error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading results: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/delete_jobs', methods=['POST'])
@login_required
def bulk_delete_jobs():
    """Bulk delete classification jobs"""
    import os
    from app.models import ClassificationJob
    from app import db
    
    try:
        job_ids = request.form.getlist('job_ids[]')
        if not job_ids:
            flash('No jobs selected for deletion.', 'warning')
            return redirect(url_for('main.results'))
        
        deleted_count = 0
        for job_id in job_ids:
            job = ClassificationJob.query.filter_by(
                id=job_id,
                user_id=current_user.id  # Security: only delete own jobs
            ).first()
            
            if job:
                # Delete associated files
                files_to_delete = []
                if job.input_kobo_path and os.path.exists(job.input_kobo_path):
                    files_to_delete.append(job.input_kobo_path)
                if job.input_raw_path and os.path.exists(job.input_raw_path):
                    files_to_delete.append(job.input_raw_path)
                if job.output_kobo_path and os.path.exists(job.output_kobo_path):
                    files_to_delete.append(job.output_kobo_path)
                if job.output_raw_path and os.path.exists(job.output_raw_path):
                    files_to_delete.append(job.output_raw_path)
                
                # Delete database record (cascade will delete variables)
                db.session.delete(job)
                deleted_count += 1
                
                # Delete files after successful db deletion
                for file_path in files_to_delete:
                    try:
                        os.remove(file_path)
                        print(f"[INFO] Deleted file: {file_path}")
                    except Exception as e:
                        print(f"[WARNING] Failed to delete file {file_path}: {e}")
        
        db.session.commit()
        
        if deleted_count > 0:
            flash(f'Successfully deleted {deleted_count} job(s).', 'success')
        else:
            flash('No jobs were deleted.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Bulk delete failed: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error deleting jobs: {str(e)}', 'error')
    
    return redirect(url_for('main.results'))


@main_bp.route('/admin/analytics')
@login_required
def admin_analytics():
    """Admin Analytics Dashboard - Super Admin Only"""
    from app.models import ClassificationJob, ClassificationVariable, User
    from sqlalchemy import func, desc
    
    # Check if user is super admin
    if not current_user.is_super_admin:
        flash('Access denied. Super Admin only.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get all completed jobs (all users)
        all_jobs = ClassificationJob.query.filter_by(status='completed').all()
        
        # Calculate global statistics
        total_jobs = len(all_jobs)
        total_responses = sum(job.total_responses or 0 for job in all_jobs)
        total_variables = sum(job.total_variables or 0 for job in all_jobs)
        total_duration_seconds = sum(job.duration_seconds or 0 for job in all_jobs)
        
        # Averages
        avg_variables_per_job = total_variables / total_jobs if total_jobs > 0 else 0
        avg_duration_per_job = total_duration_seconds / total_jobs if total_jobs > 0 else 0
        avg_responses_per_var = total_responses / total_variables if total_variables > 0 else 0
        
        # Get unique active users
        active_user_ids = set(job.user_id for job in all_jobs)
        total_active_users = len(active_user_ids)
        
        # Calculate user statistics manually (can't use property in SQL)
        user_stats = []
        for user_id in active_user_ids:
            user = User.query.get(user_id)
            if not user:
                continue
            
            # Get jobs for this user
            user_jobs = [job for job in all_jobs if job.user_id == user_id]
            
            # Calculate stats
            job_count = len(user_jobs)
            total_vars = sum(job.total_variables or 0 for job in user_jobs)
            total_resp = sum(job.total_responses or 0 for job in user_jobs)
            total_duration = sum(job.duration_seconds or 0 for job in user_jobs)
            avg_duration = total_duration / job_count if job_count > 0 else 0
            last_activity = max((job.completed_at for job in user_jobs if job.completed_at), default=None)
            
            user_stats.append({
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'job_count': job_count,
                'total_vars': total_vars,
                'total_resp': total_resp,
                'avg_duration': avg_duration,
                'last_activity': last_activity
            })
        
        # Sort by job count descending
        user_stats.sort(key=lambda x: x['job_count'], reverse=True)
        
        # Find rankings
        most_active_user = user_stats[0] if user_stats else None
        fastest_user = min(user_stats, key=lambda x: x['avg_duration']) if user_stats else None
        largest_project = max(all_jobs, key=lambda x: x.total_responses or 0) if all_jobs else None
        
        return render_template('admin_analytics.html',
            total_jobs=total_jobs,
            total_responses=total_responses,
            total_variables=total_variables,
            total_duration_hours=total_duration_seconds / 3600,
            avg_variables_per_job=avg_variables_per_job,
            avg_duration_per_job=avg_duration_per_job,
            avg_responses_per_var=avg_responses_per_var,
            total_active_users=total_active_users,
            most_active_user=most_active_user,
            fastest_user=fastest_user,
            largest_project=largest_project,
            user_stats=user_stats
        )
        
    except Exception as e:
        print(f"[ERROR] Admin analytics error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/admin/user-jobs/<int:user_id>')
@login_required
def admin_user_jobs(user_id):
    """View all jobs for a specific user - Super Admin Only"""
    from app.models import ClassificationJob, User
    from sqlalchemy import desc
    
    # Check if user is super admin
    if not current_user.is_super_admin:
        flash('Access denied. Super Admin only.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get user info
        user = User.query.get_or_404(user_id)
        
        # Get all completed jobs for this user
        jobs = ClassificationJob.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(desc(ClassificationJob.completed_at)).all()
        
        return render_template('admin_user_jobs.html',
            user=user,
            jobs=jobs
        )
        
    except Exception as e:
        print(f"[ERROR] Admin user jobs error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading user jobs: {str(e)}', 'error')
        return redirect(url_for('main.admin_analytics'))


@main_bp.route('/results/<int:job_id>')
@login_required
def view_result(job_id):
    """View detailed results for a specific job"""
    import json
    from app.models import ClassificationJob
    
    try:
        # Get specific job
        job = ClassificationJob.query.filter_by(
            id=job_id,
            user_id=current_user.id
        ).first()
        
        if not job:
            flash('Classification job not found.', 'error')
            return redirect(url_for('main.results'))
        
        # Get results from database
        results_summary = json.loads(job.results_summary) if job.results_summary else {}
        
        # Add job info
        results_summary['job_info'] = {
            'job_id': job.job_id,
            'created_at': job.created_at.strftime('%Y-%m-%d %H:%M:%S') if job.created_at else None,
            'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M:%S') if job.completed_at else None,
            'duration': job.duration_seconds,
            'original_raw_filename': job.original_raw_filename,
            'output_raw_filename': job.output_raw_filename,
            'output_kobo_filename': job.output_kobo_filename
        }
        
        return render_template('view_result.html', results=results_summary, job=job)
        
    except Exception as e:
        print(f"[ERROR] View result error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading result details: {str(e)}', 'error')
        return redirect(url_for('main.results'))


@main_bp.route('/download-file/<path:filename>')
@login_required
def download_file(filename):
    """Download classified Excel files (legacy - single file)"""
    import os
    from flask import send_from_directory
    
    # Security: Only allow downloads from uploads directory
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'files', 'uploads')
    
    # Get just the filename without path
    safe_filename = os.path.basename(filename)
    
    filepath = os.path.join(uploads_dir, safe_filename)
    
    if not os.path.exists(filepath):
        flash(f'File not found: {safe_filename}', 'error')
        return redirect(url_for('main.results'))
    
    return send_from_directory(
        uploads_dir, 
        safe_filename,
        as_attachment=True
    )

@main_bp.route('/download-job/<int:job_id>')
@login_required
def download_job(job_id):
    """Download classification job results as ZIP (2 files: kobo + raw)"""
    import os
    import zipfile
    from io import BytesIO
    from flask import send_file
    from app.models import ClassificationJob
    
    # Get job
    job = ClassificationJob.query.filter_by(id=job_id, user_id=current_user.id).first()
    
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('main.results'))
    
    # Check if download still available (24 hours)
    if not job.is_download_available:
        flash('Download expired. Files are only available for 24 hours after completion.', 'warning')
        return redirect(url_for('main.results'))
    
    # Check if output files exist
    if not job.output_kobo_path or not job.output_raw_path:
        flash('Output files not found', 'error')
        return redirect(url_for('main.results'))
    
    if not os.path.exists(job.output_kobo_path) or not os.path.exists(job.output_raw_path):
        flash('Output files not found on server', 'error')
        return redirect(url_for('main.results'))
    
    # Create ZIP in memory
    memory_file = BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add kobo file
        zf.write(job.output_kobo_path, arcname=job.output_kobo_filename)
        # Add raw file
        zf.write(job.output_raw_path, arcname=job.output_raw_filename)
    
    memory_file.seek(0)
    
    # Generate ZIP filename with original name + timestamp
    import re
    original_base = re.sub(r'\d+\.xlsx$', '', job.original_raw_filename or 'results')
    zip_filename = f"classified_{original_base}_{job.completed_at.strftime('%Y%m%d_%H%M%S')}.zip"
    
    response = send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )
    
    # Add cache control headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@main_bp.route('/admin/settings')
@login_required
def admin_settings():
    """Admin settings page"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.models import SystemSettings
    
    # Get current settings with defaults
    openai_api_key = SystemSettings.get_setting('openai_api_key', os.getenv('OPENAI_API_KEY', ''))
    openai_model = SystemSettings.get_setting('openai_model', 'gpt-4o-mini')
    
    # Brevo email settings
    brevo_api_key = SystemSettings.get_setting('brevo_api_key', os.getenv('BREVO_API_KEY', ''))
    brevo_sender_email = SystemSettings.get_setting('brevo_sender_email', 'msurvey@markplusinc.com')
    brevo_sender_name = SystemSettings.get_setting('brevo_sender_name', 'InsightCoder Platform')
    
    # Get invalid patterns
    default_patterns = """ta
t.a
tidak ada
tdk ada
tdkada
tidakada
tidak tahu
tdk tahu
tdktahu
tidaktahu
tidak tau
tdk tau
tdktau
tidaktau
n/a
na
none
-
--
---
tidak
tdk
kosong
empty
tidak ada jawaban
tidak ada saran
belum ada
belum
nothing"""
    
    invalid_patterns = SystemSettings.get_setting('invalid_patterns', default_patterns)
    invalid_category = SystemSettings.get_setting('invalid_category', 'Tidak Ada Jawaban')
    invalid_code = SystemSettings.get_setting('invalid_code', '99')
    max_categories = SystemSettings.get_setting('max_categories', '10')
    
    # Multi-label settings
    enable_multi_label = SystemSettings.get_setting('enable_multi_label', 'true')
    min_category_confidence = SystemSettings.get_setting('min_category_confidence', '0.6')
    max_categories_per_response = SystemSettings.get_setting('max_categories_per_response', '3')
    single_category_threshold = SystemSettings.get_setting('single_category_threshold', '0.92')
    
    # AI Prompts
    default_prompt_multi = """Instruksi MULTI-LABEL CLASSIFICATION:

SANGAT PENTING: Jawaban responden BISA mengandung MULTIPLE tema sekaligus!

Analisis SETIAP jawaban dengan cermat:
1. Identifikasi SEMUA tema/topik yang disebutkan dalam jawaban
2. Jika jawaban menyebutkan 2+ tema berbeda (misal: "harga mahal DAN pelayanan buruk"), WAJIB assign ke SEMUA kategori yang relevan
3. Berikan confidence score (0.0-1.0) untuk SETIAP kategori yang terdeteksi
4. Hanya include kategori dengan confidence ≥ {min_category_confidence}
5. Maksimal {max_categories_per_response} kategori per jawaban
6. EXCEPTION: Jika ada 1 kategori dengan confidence ≥ {single_category_threshold} (very dominant), gunakan HANYA kategori tersebut
7. Jika tidak ada yang cocok → "Other"

CONTOH:
- "Harga mahal dan antrian panjang" → [Pilihan Pembayaran, Jadwal dan Keberangkatan]
- "Tambah metode pembayaran, penambahan jam" → [Pilihan Pembayaran, Jadwal dan Keberangkatan]  
- "Aplikasi error dan CS tidak responsif" → [Perbaikan Aplikasi, Layanan Pelanggan]
- "Harga sangat sangat mahal sekali" → [Pilihan Pembayaran] (single dominant theme)"""
    
    default_prompt_single = """Instruksi SINGLE-LABEL CLASSIFICATION:

Pilih SATU kategori yang PALING relevan untuk setiap jawaban:
1. Analisis tema utama dari jawaban responden
2. Pilih kategori yang paling tepat menggambarkan maksud utama jawaban
3. Berikan confidence score (0.0-1.0)
4. Hanya assign jika confidence ≥ {min_category_confidence}
5. Jika tidak ada yang cocok → "Other"

CONTOH:
- "Harga terlalu mahal" → Pilihan Pembayaran
- "Jadwal tidak sesuai" → Jadwal dan Keberangkatan
- "Aplikasi sering error" → Perbaikan Aplikasi"""
    
    prompt_multi_label = SystemSettings.get_setting('prompt_multi_label', default_prompt_multi)
    prompt_single_label = SystemSettings.get_setting('prompt_single_label', default_prompt_single)
    
    # Parallel Processing settings
    enable_parallel_processing = SystemSettings.get_setting('enable_parallel_processing', os.getenv('ENABLE_PARALLEL_PROCESSING', 'true'))
    parallel_max_workers = SystemSettings.get_setting('parallel_max_workers', os.getenv('PARALLEL_MAX_WORKERS', '5'))
    rate_limit_delay = SystemSettings.get_setting('rate_limit_delay', os.getenv('RATE_LIMIT_DELAY', '0.1'))
    
    return render_template('admin_settings.html',
                         openai_api_key=openai_api_key,
                         openai_model=openai_model,
                         brevo_api_key=brevo_api_key,
                         brevo_sender_email=brevo_sender_email,
                         brevo_sender_name=brevo_sender_name,
                         invalid_patterns=invalid_patterns,
                         invalid_category=invalid_category,
                         invalid_code=invalid_code,
                         max_categories=max_categories,
                         enable_multi_label=enable_multi_label,
                         min_category_confidence=min_category_confidence,
                         max_categories_per_response=max_categories_per_response,
                         single_category_threshold=single_category_threshold,
                         prompt_multi_label=prompt_multi_label,
                         prompt_single_label=prompt_single_label,
                         enable_parallel_processing=enable_parallel_processing,
                         parallel_max_workers=parallel_max_workers,
                         rate_limit_delay=rate_limit_delay)

@main_bp.route('/admin/settings/save', methods=['POST'])
@login_required
def save_settings():
    """Save admin settings"""
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    from app.models import SystemSettings
    
    setting_type = request.form.get('setting_type')
    
    try:
        if setting_type == 'openai':
            # Save OpenAI settings
            api_key = request.form.get('openai_api_key')
            model = request.form.get('openai_model')
            
            SystemSettings.set_setting('openai_api_key', api_key, 'OpenAI API Key')
            SystemSettings.set_setting('openai_model', model, 'OpenAI Model')
            
            # Also update .env file
            update_env_file('OPENAI_API_KEY', api_key)
            
            flash('OpenAI settings saved successfully!', 'success')
        
        elif setting_type == 'brevo':
            # Save Brevo email settings
            brevo_api_key = request.form.get('brevo_api_key', '')
            brevo_sender_email = request.form.get('brevo_sender_email', 'msurvey@markplusinc.com')
            brevo_sender_name = request.form.get('brevo_sender_name', 'InsightCoder Platform')
            
            SystemSettings.set_setting('brevo_api_key', brevo_api_key, 'Brevo API Key')
            SystemSettings.set_setting('brevo_sender_email', brevo_sender_email, 'Brevo Sender Email')
            SystemSettings.set_setting('brevo_sender_name', brevo_sender_name, 'Brevo Sender Name')
            
            # Also update .env file
            if brevo_api_key:
                update_env_file('BREVO_API_KEY', brevo_api_key)
            
            flash('Brevo email settings saved successfully!', 'success')
            
        elif setting_type == 'invalid_patterns':
            # Save invalid patterns
            patterns = request.form.get('invalid_patterns')
            SystemSettings.set_setting('invalid_patterns', patterns, 'Invalid Response Patterns')
            flash('Invalid response patterns saved successfully!', 'success')
            
        elif setting_type == 'classification':
            # Save classification settings
            invalid_category = request.form.get('invalid_category')
            invalid_code = request.form.get('invalid_code')
            max_categories = request.form.get('max_categories')
            
            # Multi-label settings
            enable_multi_label = request.form.get('enable_multi_label')
            min_category_confidence = request.form.get('min_category_confidence')
            max_categories_per_response = request.form.get('max_categories_per_response')
            single_category_threshold = request.form.get('single_category_threshold')
            
            SystemSettings.set_setting('invalid_category', invalid_category, 'Invalid Category Label')
            SystemSettings.set_setting('invalid_code', invalid_code, 'Invalid Response Code')
            SystemSettings.set_setting('max_categories', max_categories, 'Max Categories')
            
            SystemSettings.set_setting('enable_multi_label', enable_multi_label, 'Enable Multi-Label Classification')
            SystemSettings.set_setting('min_category_confidence', min_category_confidence, 'Min Category Confidence')
            SystemSettings.set_setting('max_categories_per_response', max_categories_per_response, 'Max Categories Per Response')
            SystemSettings.set_setting('single_category_threshold', single_category_threshold, 'Single Category Threshold')
            
            # Also update .env file for threshold
            update_env_file('SINGLE_CATEGORY_THRESHOLD', single_category_threshold)
            
            flash('Classification settings saved successfully!', 'success')
            
        elif setting_type == 'ai_prompts':
            # Save AI prompts
            prompt_multi_label = request.form.get('prompt_multi_label')
            prompt_single_label = request.form.get('prompt_single_label')
            
            SystemSettings.set_setting('prompt_multi_label', prompt_multi_label, 'Multi-Label Prompt')
            SystemSettings.set_setting('prompt_single_label', prompt_single_label, 'Single-Label Prompt')
            
            flash('AI prompts saved successfully!', 'success')
        
        elif setting_type == 'parallel':
            # Save Parallel Processing settings
            enable_parallel = 'true' if request.form.get('enable_parallel_processing') else 'false'
            max_workers = request.form.get('parallel_max_workers', '5')
            delay = request.form.get('rate_limit_delay', '0.1')
            
            SystemSettings.set_setting('enable_parallel_processing', enable_parallel, 'Enable Parallel Processing')
            SystemSettings.set_setting('parallel_max_workers', max_workers, 'Number of Parallel Workers')
            SystemSettings.set_setting('rate_limit_delay', delay, 'Rate Limit Delay (seconds)')
            
            # Also update .env file
            update_env_file('ENABLE_PARALLEL_PROCESSING', enable_parallel)
            update_env_file('PARALLEL_MAX_WORKERS', max_workers)
            update_env_file('RATE_LIMIT_DELAY', delay)
            
            flash(f'Parallel processing settings saved! ({max_workers} workers, {delay}s delay)', 'success')
    
    except Exception as e:
        flash(f'Error saving settings: {str(e)}', 'error')
    
    return redirect(url_for('main.admin_settings'))

def update_env_file(key, value):
    """Update .env file with new value"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                key_found = True
                break
        
        if not key_found:
            lines.append(f'{key}={value}\n')
        
        with open(env_path, 'w') as f:
            f.writelines(lines)

@main_bp.route('/logo/<filename>')
def serve_logo(filename):
    """Serve logo file"""
    from flask import send_from_directory
    logo_dir = os.path.join(Config.UPLOAD_FOLDER, 'logos')
    return send_from_directory(logo_dir, filename)

@main_bp.route('/profile-photo/<filename>')
def serve_profile_photo(filename):
    """Serve profile photo file"""
    from flask import send_from_directory
    profile_photos_dir = os.path.join(Config.UPLOAD_FOLDER, 'profile_photos')
    return send_from_directory(profile_photos_dir, filename)

@main_bp.route('/logo/upload', methods=['GET', 'POST'])
@login_required
def logo_upload():
    """Logo upload page (Admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.models import SystemSettings
    from werkzeug.utils import secure_filename
    
    # Get current logo filename
    logo_filename = SystemSettings.get_setting('logo_filename', None)
    logo_url = url_for('main.serve_logo', filename=logo_filename) if logo_filename else None
    
    if request.method == 'POST':
        try:
            if 'logo_file' not in request.files:
                flash('No file uploaded', 'error')
                return redirect(url_for('main.logo_upload'))
            
            file = request.files['logo_file']
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('main.logo_upload'))
            
            # Validate file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            if file_ext not in allowed_extensions:
                flash(f'Invalid file type. Allowed: {", ".join(allowed_extensions)}', 'error')
                return redirect(url_for('main.logo_upload'))
            
            # Check file size (5MB limit)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            if file_size > 5 * 1024 * 1024:
                flash('File size exceeds 5MB limit', 'error')
                return redirect(url_for('main.logo_upload'))
            
            # Create upload directory if not exists
            upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'logos')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f'logo_{datetime.now().strftime("%Y%m%d%H%M%S")}.{file_ext}'
            filepath = os.path.join(upload_dir, unique_filename)
            
            # Save file
            file.save(filepath)
            
            # Delete old logo if exists
            if logo_filename:
                old_filepath = os.path.join(upload_dir, logo_filename)
                if os.path.exists(old_filepath):
                    try:
                        os.remove(old_filepath)
                    except:
                        pass
            
            # Save only filename (not full path)
            SystemSettings.set_setting('logo_filename', unique_filename, 'Company Logo Filename')
            
            # Auto-generate favicon and OG image
            try:
                from generate_favicon import generate_favicon_from_logo
                result = generate_favicon_from_logo(filepath, output_dir='app/static')
                if result:
                    print(f"✅ Generated {len(result)} favicon files", flush=True)
                    flash('Logo uploaded successfully! Favicon and preview images generated.', 'success')
                else:
                    flash('Logo uploaded successfully! (Favicon generation failed)', 'warning')
            except Exception as e:
                print(f"⚠️ Favicon generation error: {str(e)}", flush=True)
                flash('Logo uploaded successfully! (Favicon generation failed)', 'warning')
            
            return redirect(url_for('main.logo_upload'))
            
        except Exception as e:
            flash(f'Error uploading logo: {str(e)}', 'error')
            return redirect(url_for('main.logo_upload'))
    
    return render_template('logo_upload.html', logo_url=logo_url)

@main_bp.route('/logo/delete', methods=['POST'])
@login_required
def logo_delete():
    """Delete logo (Admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.models import SystemSettings
    
    try:
        logo_filename = SystemSettings.get_setting('logo_filename', None)
        if logo_filename:
            logo_path = os.path.join(Config.UPLOAD_FOLDER, 'logos', logo_filename)
            if os.path.exists(logo_path):
                os.remove(logo_path)
        
        SystemSettings.set_setting('logo_filename', None, 'Company Logo Filename')
        flash('Logo deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting logo: {str(e)}', 'error')
    
    return redirect(url_for('main.logo_upload'))

@main_bp.route('/favicon.ico')
@main_bp.route('/favicon-16x16.png')
@main_bp.route('/favicon-32x32.png')
@main_bp.route('/apple-touch-icon.png')
def serve_favicon():
    """Serve favicon from static directory"""
    try:
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static')
        
        # Determine which file based on request path
        if 'favicon-16x16' in request.path:
            filename = 'favicon-16x16.png'
        elif 'favicon-32x32' in request.path:
            filename = 'favicon-32x32.png'
        elif 'apple-touch-icon' in request.path:
            filename = 'apple-touch-icon.png'
        else:
            filename = 'favicon.ico'
        
        filepath = os.path.join(static_dir, filename)
        
        # If favicon not found, try to generate from logo
        if not os.path.exists(filepath):
            logo_filename = SystemSettings.get_setting('logo_filename', None)
            if logo_filename:
                logo_path = os.path.join(Config.UPLOAD_FOLDER, 'logos', logo_filename)
                if os.path.exists(logo_path):
                    print(f"🔨 Generating favicon on-the-fly...", flush=True)
                    from generate_favicon import generate_favicon_from_logo
                    generate_favicon_from_logo(logo_path, output_dir=static_dir)
        
        # Serve file if exists
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/x-icon' if filename.endswith('.ico') else 'image/png')
        
        # Fallback: return 204 No Content
        return '', 204
        
    except Exception as e:
        print(f"⚠️ Error serving favicon: {str(e)}", flush=True)
        return '', 204

@main_bp.route('/og-image.png')
def serve_og_image():
    """Serve Open Graph preview image"""
    try:
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static')
        og_path = os.path.join(static_dir, 'og-image.png')
        
        # If OG image not found, try to generate from logo
        if not os.path.exists(og_path):
            logo_filename = SystemSettings.get_setting('logo_filename', None)
            if logo_filename:
                logo_path = os.path.join(Config.UPLOAD_FOLDER, 'logos', logo_filename)
                if os.path.exists(logo_path):
                    print(f"🔨 Generating OG image on-the-fly...", flush=True)
                    from generate_favicon import generate_favicon_from_logo
                    generate_favicon_from_logo(logo_path, output_dir=static_dir)
        
        # Serve file if exists
        if os.path.exists(og_path):
            return send_file(og_path, mimetype='image/png')
        
        # Fallback: return 204 No Content
        return '', 204
        
    except Exception as e:
        print(f"⚠️ Error serving OG image: {str(e)}", flush=True)
        return '', 204

@main_bp.route('/users')
@login_required
def users():
    """User management page (Admin only)"""
    if not current_user.is_admin:
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=all_users)

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    from werkzeug.utils import secure_filename
    import os
    
    if request.method == 'POST':
        if 'profile_photo' not in request.files:
            flash('No file selected', 'warning')
            return redirect(url_for('main.profile'))
        
        file = request.files['profile_photo']
        
        if file.filename == '':
            flash('No file selected', 'warning')
            return redirect(url_for('main.profile'))
        
        if file:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            if file_ext not in allowed_extensions:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF', 'danger')
                return redirect(url_for('main.profile'))
            
            # Create profile_photos directory if not exists
            profile_photos_dir = os.path.join(Config.UPLOAD_FOLDER, 'profile_photos')
            os.makedirs(profile_photos_dir, exist_ok=True)
            
            # Generate unique filename
            unique_filename = f"profile_{current_user.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
            file_path = os.path.join(profile_photos_dir, unique_filename)
            
            # Save image
            try:
                file.save(file_path)
                
                # Delete old profile photo if exists
                if current_user.profile_photo:
                    old_photo_path = os.path.join(profile_photos_dir, current_user.profile_photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                
                # Update user profile_photo field
                current_user.profile_photo = unique_filename
                db.session.commit()
                
                flash('Profile photo updated successfully!', 'success')
                return redirect(url_for('main.profile'))
                
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'danger')
                return redirect(url_for('main.profile'))
    
    return render_template('profile.html')

@main_bp.route('/api/status')
@login_required
def api_status():
    """API endpoint for checking status"""
    return jsonify({
        'status': 'ok',
        'user': current_user.username,
        'message': 'API is working'
    })

@main_bp.route('/api/test-brevo', methods=['POST'])
@login_required
def test_brevo():
    """Test Brevo API connection"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        from app.email_service import EmailService
        
        # Get API key from request
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({'success': False, 'message': 'API key is required'})
        
        # Temporarily save to test
        from app.models import SystemSettings
        old_key = SystemSettings.get_setting('brevo_api_key', '')
        SystemSettings.set_setting('brevo_api_key', api_key, 'Brevo API Key')
        
        # Test connection
        email_service = EmailService()
        success, message = email_service.test_connection()
        
        # Restore old key if test failed
        if not success and old_key:
            SystemSettings.set_setting('brevo_api_key', old_key, 'Brevo API Key')
        
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/request-password-otp', methods=['POST'])
@login_required
def request_password_otp():
    """Request OTP for password change from profile"""
    try:
        from app.models import OTPToken
        from app.email_service import EmailService
        
        # Create OTP
        otp = OTPToken.create_otp(current_user.id, expiry_minutes=10)
        
        # Send email with app context
        email_service = EmailService()
        success, message = email_service.send_otp_email(
            recipient_email=current_user.email,
            recipient_name=current_user.full_name or current_user.username,
            otp_code=otp.code
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Verification code sent to {current_user.email}. Please check your inbox.'
            })
        else:
            # Log error for debugging
            print(f"[ERROR] Failed to send OTP to {current_user.email}: {message}")
            return jsonify({
                'success': False,
                'message': f'Failed to send email: {message}'
            })
            
    except Exception as e:
        print(f"[ERROR] Exception in request_password_otp: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@main_bp.route('/api/verify-otp-change-password', methods=['POST'])
@login_required
def verify_otp_change_password():
    """Verify OTP and change password"""
    try:
        from app.models import OTPToken
        from app.email_service import EmailService
        
        # Get form data
        otp_code = request.json.get('otp_code', '').strip()
        new_password = request.json.get('new_password', '').strip()
        confirm_password = request.json.get('confirm_password', '').strip()
        
        # Validate inputs
        if not otp_code or not new_password or not confirm_password:
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            })
        
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            })
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            })
        
        # Verify OTP
        valid, message, otp = OTPToken.verify_otp(current_user.id, otp_code)
        
        if not valid:
            return jsonify({
                'success': False,
                'message': message
            })
        
        # Change password
        current_user.set_password(new_password)
        otp.mark_as_used()
        db.session.commit()
        
        # Send confirmation email
        email_service = EmailService()
        email_service.send_password_changed_notification(
            recipient_email=current_user.email,
            recipient_name=current_user.full_name or current_user.username
        )
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully! Please use your new password for future logins.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })
