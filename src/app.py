
#path parameter - gets us the value that is unique to the id provided in the url

# QUERY PARAMETERS - optional parameters that can be passed in the url after the ? symbol
from typing import Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends

from src.schemas import PostCreate
from src.db import Post, create_db_and_tables, get_async_session  

from sqlalchemy.ext.asyncio import AsyncSession

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield



app = FastAPI(lifespan=lifespan)

@app.post("/upload/", response_model=Post)
async def upload_post(file: UploadFile = File(...), title: str = Form(...), content: str = Form(...)):
    async with get_async_session() as session:
        post = Post(title=title, content=content)
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post