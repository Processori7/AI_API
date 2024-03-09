from http.client import HTTPException
from typing import Any
import uvicorn
from aiohttp import ClientError
from fastapi import FastAPI, HTTPException
from freeGPT import AsyncClient
from pydantic import BaseModel
from starlette.responses import RedirectResponse

# uvicorn main:app --reload

# Initialize the app
app = FastAPI()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": f"An HTTP error occurred: {exc}"}

@app.exception_handler(ClientError)
async def client_error_handler(request, exc):
    return {"error": f"A client error occurred: {exc}"}

async def main(prompt):
    while True:
        try:
            resp = await AsyncClient.create_completion("gpt3", prompt)
            return resp
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get('/', response_class=RedirectResponse, status_code=307)
async def welcome():
    url = 'http://localhost:8000/docs'
    return RedirectResponse(url=url)

@app.get('/api/models')
async def getModels():
    return "Working Models: 1.gpt3"

class QuestionModel(BaseModel):
    question: str

@app.post("/api/gpt/ans")
async def getAnswer(data: QuestionModel) -> Any:
    # Теперь вопрос извлекается из тела запроса
    question = data.question

    try:
        result = await main(question)
        return {"result": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
