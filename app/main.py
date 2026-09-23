from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
import app.models
from app.routers import auth, barbers, barbershops, explore, awards, subscriptions

# Crea todas las tablas en la base de datos automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GroomGrid API",
    description="Backend API para la plataforma SaaS de barberos y barberías en México",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(barbers.router)
app.include_router(barbershops.router)
app.include_router(explore.router)
app.include_router(awards.router)
app.include_router(subscriptions.router)

@app.get("/")
def read_root():
    return {
        "project": "GroomGrid API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}