from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.routes.auth import router as auth_router
from app.api.routes.trackable import router as trackable_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, tags=["home"])
async def root():
    with open("app/static/interface.html", "r") as interface:
        return interface.read()

app.include_router(auth_router)
app.include_router(trackable_router)