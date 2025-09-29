from flask import Blueprint, request, jsonify
from usecases.evaluate_usecase import evaluate, upload, evaluation_result
from flask_jwt_extended import jwt_required

bp = Blueprint('evaluation', __name__)

@bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_endpoint():
    title = request.form.get('title')
    job_context = request.form.get('job_context')
    rubric_context = request.form.get('rubric_context')

    if not title or not job_context or not rubric_context:
        return jsonify({"error": "Missing form fields"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "Missing form field 'file'"}), 400

    f = request.files.get('file')
    if not f or f.filename == '':
        return jsonify({"error": "No file provided or empty filename"}), 400

    try:
        upload_id = upload(title, f.stream, job_context, rubric_context)
        return jsonify({"status": "uploaded", "id": upload_id}), 201
    except Exception as e:
        return jsonify({"error": "Failed to upload file", "detail": str(e)}), 500

@bp.route("/evaluate", methods=["POST"])
@jwt_required()
def evaluate_endpoint():
    id = request.json.get('id')
    if not id:
        return jsonify({"error": "Missing field 'id'"}), 400

    # Call the asynchronous evaluation function
    result = evaluate(id)
    return jsonify(result), 202

@bp.route("/result/<id>", methods=["GET"])
@jwt_required()
def get_evaluation_result(id):
    try:
        result = evaluation_result(id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Failed to get evaluation result", "detail": str(e)}), 500