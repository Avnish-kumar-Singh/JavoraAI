import multiprocessing
import os

workers = max(2, multiprocessing.cpu_count() // 2)
worker_class = "uvicorn.workers.UvicornWorker"
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
keepalive = 5
timeout = 180
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
