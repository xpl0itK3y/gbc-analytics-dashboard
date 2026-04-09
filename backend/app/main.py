from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import orders, stats

app = FastAPI(
    title="GBC Analytics Dashboard",
    description="Mini order management dashboard API",
    version="1.0.0",
)

# CORS — allow the Vue dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders.router)
app.include_router(stats.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
