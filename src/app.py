from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from datetime import datetime, timezone
from src.schemas import PostCreate
from src.db import Post, create_db_and_tables, get_async_session  

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from src.images import imagekit
import anyio  # Used to safely run synchronous file I/O in async endpoints
import shutil
import os
import tempfile

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
    caption: str = Form(""), 
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try:
        # 1. Create temp file safely
        suffix = os.path.splitext(file.filename)[1] if file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            # Offload heavy synchronous file copying to a separate thread
            await anyio.to_thread.run_sync(shutil.copyfileobj, file.file, temp_file)

        # Read the file bytes to pass to ImageKit
        with open(temp_file_path, "rb") as f:
            file_data = f.read()

        # 2. Upload to ImageKit using the correct modern SDK method (.files.upload)
        upload_result = await anyio.to_thread.run_sync(
            lambda: imagekit.files.upload(
                file=file_data,
                file_name=os.path.basename(file.filename or "upload"),
                folder="posts"
            )
        )

        # Validate response structure from ImageKit response object/dict
        file_url = getattr(upload_result, "url", None) or upload_result.get("url")
        file_name = getattr(upload_result, "name", None) or upload_result.get("name")

        if not file_url:
            raise HTTPException(status_code=400, detail="Image upload failed to return a URL.")

        # 3. DB Operations
        file_type = "video" if file.content_type and file.content_type.startswith("video/") else "image"
        
        post = Post(
            caption=caption, 
            url=file_url,  
            file_type=file_type, 
           
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    except Exception as e:
        # Catch unexpected errors, log them, and hand back an HTTP exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        
    finally:
        # Cleanup happens reliably no matter what went wrong above
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass # Prevent cleanup failures from masking original exceptions
        await file.close()  # FastAPIs UploadFile close is async


@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
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
        
    return {"posts": post_data}