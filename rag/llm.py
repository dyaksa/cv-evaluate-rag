from re import sub
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded
import backoff
import json

EVAL_PROMPT = """
You are an HR-tech evaluator. Rate the candidate's resume against the following Job Description and Rubric.
Return valid JSON according to the schema.

=== JOB DESCRIPTION (concise, relevant) ===
{job_ctx}

=== RUBRIC (assessment criteria) ===
{rubric_ctx}

=== RESUME (concise/extract) ===
{resume_text}

Instructions:
1) Score ‘skills_fit’, ‘experience_fit’, ‘education_fit’, ‘tools_fit’ (0..1).
2) ‘project_score’ 0..10 based on the rubric (structure, chaining, evaluation, error handling, RAG depth).
3) ‘cv_match_rate’ 0..1 combined (prioritize relevance of skills + experience).
4) ‘missing_keywords’ list of strings.
5) Write specific, actionable ‘cv_feedback’ and ‘project_feedback’.
6) ‘overall_summary’ 1-2 sentences.

JSON format:
{{
“cv_match_rate”: <float 0..1>,
‘cv_feedback’: “...”,
“project_score”: <float 0..10>,
‘project_feedback’: “...”,
“overall_summary”: “...”,
}}
"""


@backoff.on_exception(backoff.expo, (ResourceExhausted, DeadlineExceeded), max_tries=3) 
def llm_score(job_ctx: str, rubric_ctx: str, resume_text: str):
    prompt = EVAL_PROMPT.format(job_ctx=job_ctx, rubric_ctx=rubric_ctx, resume_text=resume_text)
    llm = ChatGoogleGenerativeAI(model=settings.GOOGLE_LLM_MODEL, temperature=0.2, google_api_key=settings.GOOGLE_API_KEY)
    out = llm.invoke(prompt).content
    cleanup = sub(r"```[a-zA-Z]*", "", out).strip()  # Remove any code block markers
    try:
        data = json.loads(cleanup)
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON from model: {e}\nRaw: {out[:400]}")

    return data