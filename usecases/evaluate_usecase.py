from repositories import upload_repository, evaluation_repository
from app.tasks import evaluate_cv_task
from datetime import datetime
from core.config import settings
from internal.db import SessionLocal
from model.model import Evaluation, EvaluationStatus
from pkg.minio import MinioClient
import tempfile
import uuid
import os


os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
def upload(title: str, stream: bytes, job_context: str, rubric_context: str) -> str:
    filename = title.replace(' ', '_') + datetime.now().strftime("-%Y%m%d-%H%M%S") + '.pdf'
    minio_client = MinioClient()

    with tempfile.NamedTemporaryFile(delete=True, prefix="pre_", suffix=".pdf", dir=settings.UPLOAD_FOLDER) as temp_file:
        temp_file.write(stream.read())
        save_path = temp_file.name
        object_name = f"cv-evaluation-service/resume/{filename}"
        minio_client.upload_file(save_path, object_name)

    upload_repo = upload_repository.UploadRepository()
    upload = upload_repo.create(
        title=title,
        file_path=object_name,
        job_context=job_context,
        rubric_context=rubric_context
    )

    evaluation_repo = evaluation_repository.EvaluationRepository(SessionLocal())
    evaluation = Evaluation(
        id=str(uuid.uuid4()),
        upload_id=upload.id,
        status=EvaluationStatus.uploaded
    )
    evaluation_repo.create(evaluation)

    return evaluation.id

def evaluate(id: str):
    try:
        evaluation_repo = evaluation_repository.EvaluationRepository(SessionLocal())
        exist_eval = evaluation_repo.get_by_id(id)
        if not exist_eval:
            return {"error": "Evaluation not found"}
        
        if exist_eval.status in [EvaluationStatus.processing, EvaluationStatus.completed, EvaluationStatus.queued]:
            return {"status": exist_eval.status, "id": exist_eval.id}

        exist_upload = upload_repository.UploadRepository().find_by_id(exist_eval.upload_id)
        if not exist_upload:
            return {"error": "Upload not found"}
        
        payload = {
            "evaluate_id": str(exist_eval.id),
            "title": exist_upload.title,
            "file_path": exist_upload.file_path,
            "job_context": exist_upload.job_context,
            "rubric_context": exist_upload.rubric_context
        }

        evaluate_cv_task.delay(payload)

        exist_eval.status = EvaluationStatus.queued
        updated_evaluation = evaluation_repo.update_status(exist_eval.id, EvaluationStatus.queued)

        return {"status": updated_evaluation.status, "id": updated_evaluation.id}
    except evaluate_cv_task.OperationalError as e:
        print(f"Task queueing failed: {e}")
        return {"error": f"Failed to queue evaluation task: {e}"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred"}

def evaluation_result(evaluate_id: str):
    evaluation_repo = evaluation_repository.EvaluationRepository(SessionLocal())
    evaluation = evaluation_repo.get_by_id(evaluate_id)
    if not evaluation:
        raise ValueError("Evaluation not found")

    if evaluation.status != EvaluationStatus.completed:
        return {"status": evaluation.status, "id": evaluation.id}

    result = {
        "id": evaluation.id,
        "status": evaluation.status,
        "result": {
            "cv_match_rate": evaluation.cv_match_rate,
            "cv_feedback": evaluation.cv_feedback,
            "project_score": evaluation.project_score,
            "overall_summary": evaluation.overall_summary
        }
    }
    return result