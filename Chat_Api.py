from http.client import HTTPException
from typing import Any
import uvicorn
from aiohttp import ClientError
from fastapi import FastAPI, HTTPException
from freeGPT import AsyncClient
from pydantic import BaseModel
from starlette.responses import RedirectResponse
import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 1))
        IP = s.getsockname()[0]
    except socket.error as err:
        print(f"Socket error: {err}")
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

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

@app.get('/', response_class=RedirectResponse, status_code=307, include_in_schema=False)
async def welcome():
    try:
        ip = get_local_ip()
    except Exception as e:
        return {"error": f"Failed to get local IP: {e}"}
    url = f'http://{ip}:8000/docs'
    return RedirectResponse(url=url)

@app.get('/api/models')
async def getModels():
    return "Working Model: 1.gpt3"

class QuestionModel(BaseModel):
    question: str

@app.post("/api/gpt/ans")
async def getAnswer(data: QuestionModel) -> Any:
    question = data.question
    try:
        result = await main(question)
        return {"result": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    try:
        ip = get_local_ip()
        uvicorn.run(app, host=ip, port=8000)
    except Exception as e:
        print(f"Failed to start the server: {e}")
