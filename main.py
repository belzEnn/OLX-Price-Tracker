from fastapi import FastAPI
from routers import search

app = FastAPI()

app.include_router(search.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Go to 127.0.0.1/docs"}
