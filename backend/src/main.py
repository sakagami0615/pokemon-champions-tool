from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from presentation.routers import data, recognition, prediction, party

app = FastAPI(title="Pokemon Champions Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(recognition.router)
app.include_router(prediction.router)
app.include_router(party.router)

sprites_dir = Path(__file__).parent.parent / "data" / "sprites"
sprites_dir.mkdir(parents=True, exist_ok=True)
app.mount("/sprites", StaticFiles(directory=str(sprites_dir)), name="sprites")


@app.get("/api/health")
def health():
    return {"status": "ok"}
