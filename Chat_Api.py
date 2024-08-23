from http.client import HTTPException
from typing import Any
import uvicorn
from aiohttp import ClientError
from fastapi import FastAPI, HTTPException
from webscout import WEBS as w
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

async def main(prompt, model):
    while True:
        try:
            response = w().chat(prompt, model=model)  # GPT-4.o mini, mixtral-8x7b, llama-3-70b, claude-3-haiku
            return response
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
    return "Working Model: 1.gpt-4o-mini 2.claude-3-haiku 3.llama-3-70b 4.mixtral-8x7b"

class QuestionModel(BaseModel):
    question: str
    model: str

@app.post("/api/gpt/ans")
async def getAnswer(data: QuestionModel) -> Any:
    question = data.question
    model = data.model
    try:
        result = await main(question, model)
        return {"result": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((get_local_ip(), port)) != 0

def find_free_port(start_port=8000, end_port=9000):
    for port in range(start_port, end_port):
        if is_port_free(port):
            return port
    raise RuntimeError("Ошибка! Нет свободных портов!")

if __name__ == '__main__':
    try:
        ip = get_local_ip()
        port = 8000  # Начальный порт
        if not is_port_free(port):
            print(f"Порт {port} занят, ищу свободный порт...")
            port = find_free_port(port, 9000)  # Поиск свободного порта в диапазоне
        uvicorn.run(app, host=ip, port=port)
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")
