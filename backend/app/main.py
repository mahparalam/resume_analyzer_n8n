from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.jobs import router as jobs_router
from app.routers.resumes import router as resumes_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Resume Intelligence Platform API"}


app.include_router(jobs_router)
app.include_router(resumes_router)