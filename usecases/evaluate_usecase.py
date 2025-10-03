from rag.chains import cv_extract
from rag.pdf_reader import extract_text_from_pdf
from repositories import embedding_repository, upload_repository, evaluation_repository
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from rag.llm import llm_score, EVAL_PROMPT
from langchain_google_genai import ChatGoogleGenerativeAI
from internal.redis import RedisClient
from datetime import datetime
from core.config import settings
from internal.db import SessionLocal
from model.model import Evaluation, EvaluationStatus
import time
import uuid
import os

redis_client = RedisClient()
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

def upload(title: str, stream: bytes, job_context: str, rubric_context: str) -> str:
    filename = title.replace(' ', '_') + datetime.now().strftime("-%Y%m%d-%H%M%S") + '.pdf'

    save_path = os.path.join(settings.UPLOAD_FOLDER, filename)
    with open(save_path, 'wb') as f:
        f.write(stream.read())

    upload_repo = upload_repository.UploadRepository()
    upload = upload_repo.create(
        title=title,
        file_path=save_path,
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
        "evaluate_id": exist_eval.id,
        "title": exist_upload.title,
        "file_path": exist_upload.file_path,
        "job_context": exist_upload.job_context,
        "rubric_context": exist_upload.rubric_context
    }

    redis_client.produce_message(payload)

    exist_eval.status = EvaluationStatus.queued
    updated_evaluation = evaluation_repo.update_status(exist_eval.id, EvaluationStatus.queued)

    return {"status": updated_evaluation.status, "id": updated_evaluation.id}

def evaluate_async_cv(message_id: str, payload: dict):
    try:
        title = payload.get("title", "Untitled")
        file_path = payload["file_path"]
        job_context = payload.get("job_context", "")
        rubric_context = payload.get("rubric_context", "")
        evaluate_id = payload.get("evaluate_id", "")

        if evaluate_id == "":
            raise ValueError("Missing evaluate_id in payload")

        with open(file_path, 'rb') as f:
            result = _evaluate_cv(evaluate_id, title, f, job_context, rubric_context)
        
        return True
    except Exception as e:
        print(f"Error processing message {message_id}: {e}")
        return False
    

def _evaluate_cv(evaluate_id: str, title: str, stream: bytes, job_context: str, rubric_context: str):
    try:
        embedding_repo = embedding_repository.EmbeddingRepository()

        resume_extract = extract_text_from_pdf(stream)
        resume_summary = cv_extract(resume_extract)

        embedding_repo.upsert_document_end_embedding(title=title, doc_type="resume", text=resume_summary)
        embedding_repo.upsert_document_end_embedding(title=title, doc_type="job", text=job_context)
        embedding_repo.upsert_document_end_embedding(title=title, doc_type="rubric", text=rubric_context)

        job_context, rubric_context = embedding_repo.build_context(resume_summary, top_k=4)

        if not settings.GOOGLE_API_KEY:
            print("GOOGLE_API_KEY is not set in environment variables")
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")

        prompt_template = PromptTemplate.from_template(EVAL_PROMPT)
        model = ChatGoogleGenerativeAI(model=settings.GOOGLE_LLM_MODEL, temperature=0.2, google_api_key=settings.GOOGLE_API_KEY)
        evaluation_chain = (
            RunnableLambda(lambda x: prompt_template.format_prompt(**x).to_string())  
            | model 
            | SimpleJsonOutputParser()
        )

        llm_result = evaluation_chain.invoke({
            "job_ctx": embedding_repo.top_k_similiar(resume_summary, top_k=4, where_kind="job"),
            "rubric_ctx": embedding_repo.top_k_similiar(resume_summary, top_k=4, where_kind="rubric"),
            "resume_text": resume_summary
        })

        cv_match_rate = float(llm_result.get("cv_match_rate", 0.0))
        cv_feedback = str(llm_result.get("cv_feedback", ""))
        project_score = float(llm_result.get("project_score", 0.0))
        overall_summary = str(llm_result.get("overall_summary", ""))

        evaluation_repo = evaluation_repository.EvaluationRepository(SessionLocal())
        evaluation = evaluation_repo.update_status(evaluate_id, EvaluationStatus.processing)

        time.sleep(5)

        evaluation_repo = evaluation_repository.EvaluationRepository(SessionLocal())
        evaluation = evaluation_repo.fill_results(
            evaluation_id=evaluate_id,
            cv_match_rate=cv_match_rate,
            cv_feedback=cv_feedback,
            project_score=project_score,
            overall_summary=overall_summary
        )

        if not evaluation:
            raise ValueError(f"Failed to update evaluation with id {evaluate_id}")

        return llm_result
    except Exception as e:
        print(f"Error processing message {evaluate_id}: {e}")
        raise e

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