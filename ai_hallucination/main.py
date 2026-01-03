from fastapi import FastAPI, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from database import get_session, engine
from models import Verification
from services import AIService
from contextlib import asynccontextmanager
import json
import os

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "online"}

@app.post("/api/verifications/create")
async def create_verification(
    data: dict,
    db: AsyncSession = Depends(get_session)
):
    if "text" not in data:
        raise HTTPException(status_code=400, detail="Missing 'text' field")

    try:
        raw = await AIService.analyze_text(data["text"])
        result = json.loads(raw)

        db_verification = Verification(
            input_text=data["text"],
            result=result
        )

        db.add(db_verification)
        await db.commit()
        await db.refresh(db_verification)

        return db_verification

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))
    )
