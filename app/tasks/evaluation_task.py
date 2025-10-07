from core.config import settings
from internal.db import SessionLocal
from pkg.minio import MinioClient
from model.model import  EvaluationStatus
from repositories import evaluation_repository, embedding_repository
from model.model import EvaluationResponse
from rag.chains import summarize, zhipu_cv_extractor
from rag.pdf_reader import extract_text_from_pdf
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from rag.llm import EVAL_PROMPT
from re import sub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from internal.celery import celery
import json
import tempfile

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def evaluate_cv_task(self, payload: dict):
    try:
        title = payload.get("title", "Untitled")
        file_path = payload["file_path"]
        job_context = payload.get("job_context", "")
        rubric_context = payload.get("rubric_context", "")
        evaluate_id = payload.get("evaluate_id", "")
        minio_client = MinioClient()

        if evaluate_id == "":
            raise ValueError("Missing evaluate_id in payload")
        
        with tempfile.NamedTemporaryFile(delete=True, prefix="pre_", suffix=".pdf", dir=settings.UPLOAD_FOLDER) as temp_file:
            download_success = minio_client.download_file(file_path, temp_file.name)
            if not download_success:
                raise ValueError(f"Failed to download file from MinIO: {file_path}")
            with open(temp_file.name, 'rb') as f:
                _evaluate_cv(evaluate_id, title, f, job_context, rubric_context)
        
        return True
    except Exception as e:
        print(f"Error processing message: {e}")
    

def _evaluate_cv(evaluate_id: str, title: str, stream: bytes, job_context: str, rubric_context: str):
    try:
        embedding_repo = embedding_repository.EmbeddingRepository()

        resume_extract = extract_text_from_pdf(stream)
        resume_summary = zhipu_cv_extractor(resume_extract)
        job_summary = summarize(job_context)


        _ = embedding_repo.insert_chroma_embedding(title=title, doc_type="resume", text=resume_summary)
        _ = embedding_repo.insert_chroma_embedding(title=title, doc_type="job", text=job_summary)
        _ = embedding_repo.insert_chroma_embedding(title=title, doc_type="rubric", text=rubric_context)

        job_context, rubric_context = embedding_repo.build_context_chroma(resume_summary, top_k=4)

        prompt_template = PromptTemplate.from_template(EVAL_PROMPT)

        model = ChatOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL_MODEL,
            model=settings.OPENROUTER_LLM_MODEL,
            temperature=0.2,
            max_retries=3
        )

        json_parser = JsonOutputParser(pydantic_object=EvaluationResponse)
        evaluation_chain = (
            RunnableLambda(lambda x: prompt_template.format_prompt(**x).to_string())  
            | model 
            | json_parser
        )

        llm_result = evaluation_chain.invoke({
            "job_ctx": job_context,
            "rubric_ctx": rubric_context,
            "resume_text": resume_summary
        })

        if type(llm_result) is str:
            cleanup = sub(r"```[a-zA-Z]*", "", llm_result).strip()
            llm_result = json.loads(cleanup)


        cv_match_rate = float(llm_result.get("cv_match_rate", 0.0))
        cv_feedback = str(llm_result.get("cv_feedback", ""))
        project_score = float(llm_result.get("project_score", 0.0))
        overall_summary = str(llm_result.get("overall_summary", ""))

        # Use single session for both operations
        session = SessionLocal()
        evaluation_repo = evaluation_repository.EvaluationRepository(session)
        
        try:
            evaluation = evaluation_repo.update_status(evaluate_id, EvaluationStatus.processing)
            
            evaluation = evaluation_repo.fill_results(
                evaluation_id=evaluate_id,
                cv_match_rate=cv_match_rate,
                cv_feedback=cv_feedback,
                project_score=project_score,
                overall_summary=overall_summary
            )
        finally:
            evaluation_repo.close()

        if not evaluation:
            raise ValueError(f"Failed to update evaluation with id {evaluate_id}")

        return llm_result
    except Exception as e:
        print(f"Error processing message {evaluate_id}: {e}")
        raise e