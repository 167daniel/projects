"""
main.py

Entry point for the Mini-ATM FastAPI application.

Responsibilities:
- Create FastAPI app instance
- Include the API router from api.py
- Configure any global middleware or exception handlers (minimal for now)
- Run the server when executed as a script
"""

from fastapi import FastAPI
from api import router
from storage import initialize_accounts
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_accounts()  # Initialize accounts before the server starts
    yield
    # Shutdown code can go here if needed

app = FastAPI(title="Mini-ATM API", version="1.0", lifespan=lifespan)

# include router
app.include_router(router)

# Run the server using:
# uvicorn main:app --reload
# (Reload enables auto restart on code changes for local development)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
