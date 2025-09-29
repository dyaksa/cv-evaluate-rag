import json, os, uuid
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from core.config import settings
from google.api_core.exceptions import ResourceExhausted, DeadlineExceeded
import backoff
from re import sub


@backoff.on_exception(backoff.expo, (ResourceExhausted, DeadlineExceeded), max_tries=3) 
def embed_texts(texts: list[str]) -> list[list[float]]:
    try:
        embed = GoogleGenerativeAIEmbeddings(model=settings.GOOGLE_EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY)
        return embed.embed_documents(texts)
    except Exception as e:
        raise Exception(f"Invalid error from model: {e}\n")

@backoff.on_exception(backoff.expo, (ResourceExhausted, DeadlineExceeded), max_tries=3)
def cv_extract(cv_text: str) -> str:
    llm = ChatGoogleGenerativeAI(model=settings.GOOGLE_LLM_MODEL, temperature=0.2, google_api_key=settings.GOOGLE_API_KEY)
    prompt = f"""Play the role of an HR-tech summarizer. Summarize the following resume in <=150 words
    focusing on skills, key experience (with years), tools, and project highlights."""
    msgs = [SystemMessage(content=prompt),
            HumanMessage(content=cv_text)]
    try:
        out = llm.invoke(msgs)
    except Exception as e:
        raise Exception(f"Invalid error from model: {e}\n") 
    
    return out.content

def cv_compare(profile_json: dict, job_ctx: str) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GOOGLE_LLM_MODEL, temperature=0.2, google_api_key=settings.GOOGLE_API_KEY)
    sys = f"{job_ctx}\n\n"  # inject JOB context
    msgs = [SystemMessage(content=sys + "You are evaluating CV vs JOB with cv_score format number and calculating based on parameter skills, experiences, projects, ensure consistency data response."),
            HumanMessage(content=f"CV_PROFILE_JSON:\n{json.dumps(profile_json)}\nReturn required JSON only.")]
    out = llm.invoke(msgs)
    cleanup = sub(r"```[a-zA-Z]*", "", out.content).strip() # Remove any code block markers
    return json.loads(cleanup)

def project_eval(project_text: str, rubric_ctx: str) -> dict:
    llm = ChatGoogleGenerativeAI(model=settings.GOOGLE_LLM_MODEL, temperature=0.2, google_api_key=settings.GOOGLE_API_KEY)
    sys = rubric_ctx + "\nYou are evaluating PROJECT REPORT against rubric."
    msgs = [SystemMessage(content=sys),
            HumanMessage(content=f"PROJECT_REPORT:\n{project_text}\nReturn required JSON only.")]
    out = llm.invoke(msgs)
    cleanup = sub(r"```[a-zA-Z]*", "", out.content).strip() # Remove any code block markers
    return json.loads(cleanup)

def retrieve_ctx(query: str, top_k=4) -> str:
    pass
