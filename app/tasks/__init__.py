from .evaluation_task import evaluate_cv_task
from .celery import celery

__all__ = ["evaluate_cv_task", "celery"]