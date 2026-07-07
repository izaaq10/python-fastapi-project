from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends

from datetime import datetime, timezone
from src.schemas import PostCreate
from src.db import Post, create_db_and_tables, get_async_session  

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload/")
async def upload_post(
    file: UploadFile = File(...), 
    title: str = Form(...), 
    content: str = Form(...),
    caption: str = Form(""),  # Moved to function parameters
    session: AsyncSession = Depends(get_async_session)  # Moved to function parameters
):
    # Note: Make sure your Post model has 'title' and 'content' fields if you intend to save them!
    post = Post(
        caption=caption, 
        url=file.filename, 
        file_type=file.content_type, 
        created_at=datetime.now(timezone.utc), # updated from deprecated utcnow()
        updated_at=datetime.now(timezone.utc)
    )
    
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post

@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    
    # Safely extract posts from the result scalars
    posts = result.scalars().all() 
    
    post_data = []
    for post in posts:
        post_data.append({
            "id": post.id,
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "created_at": post.created_at.isoformat(),
            "updated_at": post.updated_at.isoformat()
        })
        
    # Moved outside the for-loop so it returns all posts, not just the first one
    return {"posts": post_data}