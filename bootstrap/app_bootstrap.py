from flask import Flask
from app.controller import evaluation_bp
from internal.db import Base, engine
from internal.redis import RedisClient
from usecases.evaluate_usecase import evaluate_async_cv
from threading import Thread
from flask_jwt_extended import JWTManager
from core.config import settings
import time

from model.model import Document, Embedding, Evaluation, Upload

redis_client = RedisClient()

def init_db():
    Base.metadata.create_all(bind=engine)

def create_app():
    app = Flask(__name__)

    app.config.update({'MAX_CONTENT_LENGTH': 16 * 1024 * 1024})  # 16 MB limit
    
    # Correct parameter name is url_prefix
    # app.register_blueprint(ingest_bp, url_prefix='/api/ingest')
    JWTManager(app)
    app.register_blueprint(evaluation_bp, url_prefix='/api')

    return app

def start_redis_consumer():
    """Start Redis consumer in a separate process/thread"""
    def run_consumer():
        time.sleep(5)  # Wait for the app to be fully up
        redis_client.run(handler=evaluate_async_cv)

    consumer_thread = Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    print("Redis consumer started in a separate thread")

