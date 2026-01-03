from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from database import get_session, engine
from models import Verification, Message, Conversation
from services import AIService
import json
import os
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000)) # Render provides the port automatically
    uvicorn.run("main:app", host="0.0.0.0", port=port)

app = FastAPI()

@app.post("/api/verifications/create")
async def create_verification(data: dict, db: AsyncSession = Depends(get_session)):
    # 1. AI Analysis
    raw_result = await AIService.analyze_text(data['text'])
    result_json = json.loads(raw_result)
    
    # 2. Save to DB
    db_verif = Verification(input_text=data['text'], result=result_json)
    db.add(db_verif)
    await db.commit()
    await db.refresh(db_verif)
    return db_verif

@app.post("/api/conversations/{id}/messages")
async def chat_message(id: int, data: dict, db: AsyncSession = Depends(get_session)):
    # Save user message
    user_msg = Message(conversation_id=id, role="user", content=data['content'])
    db.add(user_msg)
    await db.commit()

    async def event_generator():
        full_response = ""
        # Fetch history and stream Gemini response
        async for chunk in AIService.stream_chat([], data['content']):
            full_response += chunk
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        # Save complete AI response to DB
        assistant_msg = Message(conversation_id=id, role="assistant", content=full_response)
        db.add(assistant_msg)
        await db.commit()
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Start-up seeding logic
@app.on_event("startup")
async def on_startup():
    # Database migration logic here
    pass