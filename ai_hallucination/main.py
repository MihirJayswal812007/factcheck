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

# 1. DATABASE SEEDING LOGIC
async def init_db():
    async with engine.begin() as conn:
        # This creates tables if they don't exist
        await conn.run_sync(SQLModel.metadata.create_all)

# 2. LIFESPAN MANAGER (Replaces old startup events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: Creating database tables...")
    await init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# 3. HEALTH CHECK (Use this to test your connection)
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_session)):
    try:
        await db.execute(select(1))
        return {"status": "online", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

@app.post("/api/verifications/create")
async def create_verification(data: dict, db: AsyncSession = Depends(get_session)):
    if 'text' not in data:
        raise HTTPException(status_code=400, detail="Missing 'text' field")
    
    # 4. AI Analysis with Error Handling
    try:
        raw_result = await AIService.analyze_text(data['text'])
        # Clean markdown if Gemini returns ```json ... ```
        clean_json = raw_result.strip().replace("```json", "").replace("```", "")
        result_json = json.loads(clean_json)
        
        # 5. Save to DB
        db_verif = Verification(input_text=data['text'], result=result_json)
        db.add(db_verif)
        await db.commit()
        await db.refresh(db_verif)
        return db_verif
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# (Keep your chat_message endpoint here...)

# Render-specific entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)