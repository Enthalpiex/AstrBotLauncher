from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union
from sentence_transformers import SentenceTransformer
import torch

app = FastAPI()

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("BAAI/bge-m3", device=device)

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str

@app.post("/v1/embeddings")
def create_embedding(request: EmbeddingRequest):
    texts = request.input if isinstance(request.input, list) else [request.input]

    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    data = [
        {
            "object": "embedding",
            "embedding": emb,
            "index": idx
        } for idx, emb in enumerate(embeddings)
    ]

    return {
        "object": "list",
        "data": data,
        "model": request.model,
        "usage": {
            "prompt_tokens": len(texts),
            "total_tokens": len(texts)
        }
    }
