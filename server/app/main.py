from fastapi import FastAPI

app = FastAPI(title="signalfeed")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Basic liveness check — confirms the API is up and responding."""
    return {"status": "ok"}
