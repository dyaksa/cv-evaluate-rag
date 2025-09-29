from flask import Flask, jsonify
from app.controller import evaluation_bp, auth_bp
from internal.db import Base, engine
from model.model import Document, Embedding, Evaluation, Upload
from internal.redis import RedisClient
from usecases.evaluate_usecase import evaluate_async_cv
from threading import Thread
from flask_jwt_extended import JWTManager
from core.config import settings
import time



redis_client = RedisClient()
jwt = JWTManager()

app = Flask(__name__)

app.config.update({'MAX_CONTENT_LENGTH': 16 * 1024 * 1024})  # 16 MB limit
    
jwt.init_app(app)
Base.metadata.create_all(bind=engine)

app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(evaluation_bp, url_prefix='/api')


@jwt.unauthorized_loader
def custom_unauthorized(err_msg):
    return jsonify({"error": "Authorization required", "code": "auth_missing"}), 401

@jwt.invalid_token_loader
def custom_invalid(err_msg):
    return jsonify({"error": "Invalid token", "code": "invalid_token"}), 401

@jwt.expired_token_loader
def custom_expired(jwt_header, jwt_payload):
    return jsonify({"error": "Token expired", "code": "token_expired"}), 401

@jwt.revoked_token_loader
def custom_revoked(jwt_header, jwt_payload):
    return jsonify({"error": "Token revoked", "code": "token_revoked"}), 401

@jwt.needs_fresh_token_loader
def custom_fresh(jwt_header, jwt_payload):
    return jsonify({"error": "Fresh token required", "code": "fresh_required"}), 401

