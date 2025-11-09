from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .schemas import QueryRequest, ChatResponse
from .rag_pipeline import RAGPipeline

app = FastAPI(title="DealZen API")
rag_pipeline = RAGPipeline()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Allows Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Main chat endpoint to receive user queries and return RAG answers.
    """
    response_data = await rag_pipeline.answer_query(request.query)
    return ChatResponse(**response_data)

