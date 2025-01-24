from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import watermark
from db import mongoDB
from auth import AuthMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

def create_app():
    mongoDB.init_app(app)
    api_router = APIRouter(prefix="/stamp-api/v1")
    api_router.include_router(watermark.router)
    
    app.include_router(api_router)

@app.get("/")
async def root():
    return {"status": "healthy"}

@app.get("/health")
async def root():
    return {"status": "healthy"}

create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
