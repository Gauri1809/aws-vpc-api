from mangum import Mangum
from fastapi import FastAPI
from app.apiRouter import router as api_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "No information available in root path"}

app.include_router(api_router)

lambda_handler = Mangum(app)