from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from langchain_core.messages import BaseMessage

from .chains import make_conversation_chain
from .config import get_config

app = FastAPI()
config = get_config()


class Message(BaseMessage, BaseModel):
    content: str
    type: str


class ChatCompletionRequestData(BaseModel):
    model: str
    messages: list[Message]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/models/")
def get_models():
    pass


# {
#   "object": "list",
#   "data": [
#     {
#       "id": "model-id-0",
#       "object": "model",
#       "created": 1686935002,
#       "owned_by": "organization-owner"
#     },
#     {
#       "id": "model-id-1",
#       "object": "model",
#       "created": 1686935002,
#       "owned_by": "organization-owner",
#     },
#     {
#       "id": "model-id-2",
#       "object": "model",
#       "created": 1686935002,
#       "owned_by": "openai"
#     },
#   ],
#   "object": "list"
# }


@app.post("/embeddings/")
def create_embeddings():
    pass


# curl https://api.openai.com/v1/embeddings \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "input": "The food was delicious and the waiter...",
#     "model": "text-embedding-ada-002",
#     "encoding_format": "float"
#   }'

# {
#   "object": "list",
#   "data": [
#     {
#       "object": "embedding",
#       "embedding": [
#         0.0023064255,
#         -0.009327292,
#         .... (1536 floats total for ada-002)
#         -0.0028842222,
#       ],
#       "index": 0
#     }
#   ],
#   "model": "text-embedding-ada-002",
#   "usage": {
#     "prompt_tokens": 8,
#     "total_tokens": 8
#   }
# }


@app.post("/completions/")
def chat_completion(req: ChatCompletionRequestData) -> str:
    selected_model_idx = -1
    for idx, llm in enumerate(config["llms"]):
        if llm["model"] == req.model:
            selected_model_idx = idx
            break
    if selected_model_idx != -1:
        llm = make_conversation_chain(config, selected_llm_index=selected_model_idx)
        response = llm(
            {"question": req.messages[-1].content, "chat_history": req.messages[:-1]},
            # callbacks=[retrieve_callback, print_callback, stdout_callback],
        )
        return response["answer"]
    else:
        return ""


def main():
    uvicorn.run(
        "llm_service.main:app",
        host=config.get("host", "127.0.0.1"),
        port=config.get("port", 5000),
        log_level="info",
    )


if __name__ == "__main__":
    main()
