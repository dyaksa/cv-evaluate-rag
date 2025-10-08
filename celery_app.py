#!/usr/bin/env python3
"""
Celery application entry point for worker processes.
This module provides the Celery app instance for running background tasks.
"""

from app.celery import celery

# Import all task modules to register them with Celery
# from app.tasks import evaluation_task

if __name__ == '__main__':
    celery.start()