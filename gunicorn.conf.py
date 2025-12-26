"""
Gunicorn Configuration for M-Coder Platform
Production WSGI server configuration
"""

# Server Socket
bind = "127.0.0.1:8000"  # Local only, nginx akan proxy
backlog = 2048

# Worker Processes
# NOTE: Using 1 worker because progress_tracker uses in-memory storage
# Multiple workers = separate memory spaces = progress tracking doesn't work
# TODO: Migrate to Redis/Database for multi-worker support
workers = 1  # Single worker for in-memory progress tracking
worker_class = "sync"
worker_connections = 1000
max_requests = 1000  # Restart worker after 1000 requests
max_requests_jitter = 50
timeout = 300  # 5 minutes (untuk classification yang lama)
keepalive = 2

# Process Naming
proc_name = "mcoder"

# Server Mechanics
daemon = False  # Supervisor akan handle daemonization
pidfile = "/tmp/gunicorn-mcoder.pid"
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "/var/log/mcoder/access.log"
errorlog = "/var/log/mcoder/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Note: Application will be in /opt/markplus/mcoder/

# Process Management
preload_app = True  # Load application code before forking workers
reload = False  # Don't reload in production

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

def on_starting(server):
    """Called just before the master process is initialized"""
    print("🚀 M-Coder Platform starting...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP"""
    print("♻️ Reloading M-Coder Platform...")

def when_ready(server):
    """Called just after the server is started"""
    print("✅ M-Coder Platform ready to serve requests!")

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    print(f"👷 Worker spawned (pid: {worker.pid})")

def worker_exit(server, worker):
    """Called just after a worker has been exited"""
    print(f"💤 Worker exited (pid: {worker.pid})")
