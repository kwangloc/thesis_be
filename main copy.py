# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class GreetRequest(BaseModel):
    name: str

@app.post("/greet")
def greet_user(request: GreetRequest):
    return {"message": f"Hello, {request.name}!"}
