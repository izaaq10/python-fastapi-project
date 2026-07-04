
#path parameter - gets us the value that is unique to the id provided in the url

# QUERY PARAMETERS - optional parameters that can be passed in the url after the ? symbol
from typing import Optional
from fastapi import FastAPI, HTTPException

from src.schemas import PostCreate

app = FastAPI()

text_posts = {
    "1": {"title": "First Post", "content": "This is the first post."},
    "2": {"title": "Second Post", "content": "This is the second post."},
    "3": {"title": "Third Post", "content": "This is the third post."},
    "4": {"title": "Fourth Post", "content": "This is the fourth post."},
    "5": {"title": "Fifth Post", "content": "This is the fifth post."},
    "6": {"title": "Sixth Post", "content": "This is the sixth post."},
    "7": {"title": "Seventh Post", "content": "This is the seventh post."},
    "8": {"title": "Eighth Post", "content": "This is the eighth post."},
    "9": {"title": "Ninth Post", "content": "This is the ninth post."},
    "10": {"title": "Tenth Post", "content": "This is the tenth post."}
}

@app.get("/posts")
async def get_all_posts(limit: Optional[int] = None):
    if limit is not None:
        return list(text_posts.values())[:limit]
    return text_posts


@app.get("/posts/{id}")
async def get_post(id: str):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts.get(id)


@app.post("/posts", status_code=201)
async def create_post(post: PostCreate) -> dict:
    new_post = {"title": post.title, "content": post.content}
    new_id = str(max(int(k) for k in text_posts.keys()) + 1) if text_posts else "1"
    text_posts[new_id] = new_post
    return {"id": new_id, **new_post}