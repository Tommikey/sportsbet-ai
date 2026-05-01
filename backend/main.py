from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import soccer, nba, nfl, tennis
import uvicorn

app = FastAPI(title="SportsBet AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(soccer.router, prefix="/api/soccer", tags=["Soccer"])
app.include_router(nba.router, prefix="/api/nba", tags=["NBA"])
app.include_router(nfl.router, prefix="/api/nfl", tags=["NFL"])
app.include_router(tennis.router, prefix="/api/tennis", tags=["Tennis"])

@app.get("/")
def root():
    return {"status": "SportsBet AI is running", "version": "1.0.0"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
