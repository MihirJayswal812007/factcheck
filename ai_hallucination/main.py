from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, SQLModel
from database import get_session, engine
from models import Verification, Message, Conversation
from services import AIService
from contextlib import asynccontextmanager
import json
import os

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This creates your 'verifications' table when Render starts the app
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "online"}

@app.post("/api/verifications/create")
async def create_verification(data: dict, db: AsyncSession = Depends(get_session)):
    try:
        raw_result = await AIService.analyze_text(data['text'])
        result_json = json.loads(raw_result)
        
        db_verif = Verification(input_text=data['text'], result=result_json)
        db.add(db_verif)
        await db.commit()
        await db.refresh(db_verif)
        return db_verif
    except Exception as e:
        print(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)