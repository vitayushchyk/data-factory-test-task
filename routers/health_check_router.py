from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from langchain_google_genai import ChatGoogleGenerativeAI

from llm.llm_client import LLMClient

health_check_router = APIRouter(tags=["Healthcheck"])

llm_client = LLMClient()
@health_check_router.get(
    "/health-check/",
    status_code=status.HTTP_200_OK,
    description="Healthcheck endpoint to check the health of the project",
)
async def _health_check():
    """Check is  the health of the project"""
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=dict(detail="ok", result="working")
    )


@health_check_router.get("/check-langsmith/gemini/")
async def check_langsmith_and_gemini():
    """
    Check if Langsmith and Gemini are working.
    """
    try:
        # llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest")

        response = llm_client.invoke("How much is 2 + 2?")
        return JSONResponse(
            status_code=status.HTTP_200_OK, content=dict(result=response.content)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
