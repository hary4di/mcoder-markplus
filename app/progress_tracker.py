"""
Progress Tracker untuk Real-time Classification Updates
"""
import time
from datetime import datetime
from threading import Lock

class ProgressTracker:
    """Thread-safe progress tracker untuk classification process"""
    
    def __init__(self):
        self.data = {}
        self.lock = Lock()
    
    def create_job(self, job_id, total_variables):
        """Create new classification job"""
        with self.lock:
            self.data[job_id] = {
                'status': 'initializing',
                'current_variable': None,
                'current_step': 'Starting classification...',
                'progress': 0,
                'total_variables': total_variables,
                'completed_variables': 0,
                'current_variable_progress': 0,
                'start_time': datetime.now().isoformat(),
                'messages': [],
                'error': None,
                'completed': False
            }
    
    def update_variable(self, job_id, variable_name, variable_index, total_variables, question_text=None):
        """Update current variable being processed"""
        with self.lock:
            if job_id in self.data:
                self.data[job_id]['current_variable'] = variable_name
                self.data[job_id]['current_variable_question'] = question_text
                self.data[job_id]['status'] = 'processing'
                self.data[job_id]['current_step'] = f'Processing variable: {variable_name}'
                # Store variable progress tracking
                self.data[job_id]['current_variable_index'] = variable_index
                self.data[job_id]['current_variable_progress'] = 0
                self.add_message(job_id, f'Starting classification for {variable_name} ({variable_index}/{total_variables})')
    
    def update_step(self, job_id, step_name, step_progress=None):
        """Update current processing step"""
        with self.lock:
            if job_id in self.data:
                self.data[job_id]['current_step'] = step_name
                if step_progress is not None:
                    self.data[job_id]['current_variable_progress'] = step_progress
                    # Calculate overall progress: (completed_vars + current_var_progress) / total_vars
                    completed = self.data[job_id]['completed_variables']
                    total = self.data[job_id]['total_variables']
                    current_progress = step_progress / 100  # Convert to 0-1 range
                    overall = int(((completed + current_progress) / total) * 100)
                    self.data[job_id]['progress'] = min(100, overall)
                self.add_message(job_id, step_name)
    
    def update_progress(self, job_id, progress, message=None):
        """Update overall progress percentage"""
        with self.lock:
            if job_id in self.data:
                self.data[job_id]['progress'] = min(100, max(0, progress))
                if message:
                    self.data[job_id]['current_step'] = message
                    self.add_message(job_id, message)
    
    def complete_variable(self, job_id, variable_name, summary):
        """Mark variable as completed"""
        with self.lock:
            if job_id in self.data:
                self.data[job_id]['completed_variables'] += 1
                completed = self.data[job_id]['completed_variables']
                total = self.data[job_id]['total_variables']
                
                msg = f'✓ {variable_name} complete: {summary["valid_classified"]} responses coded into {summary["categories_generated"]} categories'
                self.add_message(job_id, msg)
                
                # Update progress
                progress = int((completed / total) * 100)
                self.data[job_id]['progress'] = progress
    
    def complete_job(self, job_id, results):
        """Mark job as completed"""
        with self.lock:
            if job_id in self.data:
                self.data[job_id]['status'] = 'completed'
                self.data[job_id]['completed'] = True
                self.data[job_id]['progress'] = 100
                self.data[job_id]['current_step'] = 'Classification complete!'
                self.data[job_id]['results'] = results
                self.data[job_id]['end_time'] = datetime.now().isoformat()
                self.add_message(job_id, f'Classification complete! {results["total_variables"]} variables successfully processed.')
    
    def set_error(self, job_id, error_message):
        """Set error status"""
        with self.lock:
            if job_id in self.data:
                self.data[job_id]['status'] = 'error'
                self.data[job_id]['error'] = error_message
                self.data[job_id]['current_step'] = 'Error: ' + error_message
                self.add_message(job_id, f'❌ Error: {error_message}')
    
    def add_message(self, job_id, message):
        """Add log message - MUST be called from within a locked context"""
        if job_id in self.data:
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.data[job_id]['messages'].append({
                'time': timestamp,
                'text': message
            })
            # Keep only last 50 messages
            if len(self.data[job_id]['messages']) > 50:
                self.data[job_id]['messages'] = self.data[job_id]['messages'][-50:]
    
    def get_progress(self, job_id):
        """Get current progress data"""
        with self.lock:
            return self.data.get(job_id, {}).copy()
    
    def cleanup_job(self, job_id):
        """Remove job data after some time"""
        with self.lock:
            if job_id in self.data:
                del self.data[job_id]

# Global progress tracker instance
progress_tracker = ProgressTracker()
