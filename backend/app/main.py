from fastapi import FastAPI

from app.routers.jobs import router as jobs_router
from app.routers.resumes import router as resumes_router


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Resume Intelligence Platform API"}


app.include_router(jobs_router)
app.include_router(resumes_router)