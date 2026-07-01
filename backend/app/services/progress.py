from datetime import datetime

class ProgressTracker:
    def __init__(self, job_id):
        self.job_id = job_id
        self.steps = []
    
    def add_step(self, name, status, progress):
        self.steps.append({
            'step': name,
            'status': status,
            'progress': progress,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_status(self):
        return {
            'job_id': self.job_id,
            'steps': self.steps,
            'completed': all(s['status'] == 'complete' for s in self.steps)
        }