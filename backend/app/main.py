from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔥 TEM QUE SER AQUI, antes de tudo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois restringimos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# depois vem os routers
from app.routers.dashboard import router as dashboard_router
from app.routers.contracts import router as contracts_router
from app.routers.alerts import router as alerts_router

app.include_router(dashboard_router, prefix="/api")
app.include_router(contracts_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")