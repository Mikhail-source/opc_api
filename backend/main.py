import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.engine import Engine
from backend.api import tags, server, projects
from backend.ws import handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)-7s] %(name)-12s │ %(message)s")
logger = logging.getLogger("Backend")

# Глобальная переменная
engine: Engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    engine = Engine()
    logger.info("🧠 Engine initialized (NOT started). Use /api/server/start to run.")
    yield
    if engine and engine.is_running:
        logger.info("🛑 Stopping engine on shutdown...")
        engine.stop()

app = FastAPI(title="OPC Server API", version="1.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(server.router, prefix="/api/server", tags=["server"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(handler.router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health():
    return {"status": "ok", "running": engine.is_running if engine else False}

@app.get("/")
async def root():
    return {"message": "OPC Server API", "docs": "/docs", "endpoints": ["/api/tags", "/api/server", "/api/projects", "/ws/tags"]}

@app.get("/docs")
async def docs():
    # Перенаправление на стандартный Swagger UI
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/redoc")