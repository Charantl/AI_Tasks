from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut, CommentWithUser
from app.models.comment import Comment
from app.models.song import Song
from app.models.user import User
from app.db.session import get_db
from app.api.user import get_current_user
from typing import List

router = APIRouter(tags=["comments"])

@router.get("/songs/{song_id}/comments", response_model=List[CommentWithUser])
def list_song_comments(song_id: str, db: Session = Depends(get_db)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    comments = db.query(Comment).filter(Comment.song_id == song_id).order_by(Comment.created_at.desc()).all()
    result = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        result.append({
            "id": comment.id,
            "song_id": comment.song_id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
            "username": user.username if user else "Unknown"
        })
    return result

@router.post("/songs/{song_id}/comments", response_model=CommentOut)
def create_comment(song_id: str, comment_in: CommentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check if song exists
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    comment = Comment(
        user_id=current_user.id,
        song_id=song_id,
        content=comment_in.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/comments/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: str, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.patch("/comments/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: str, comment_in: CommentUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    comment.content = comment_in.content
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"} 