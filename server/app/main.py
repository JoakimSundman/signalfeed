from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="signalfeed")

app.include_router(auth.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic liveness check — confirms the API is up and responding."""
    return {"status": "ok"}
