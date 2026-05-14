from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.author import Author
from app.models.book import Book
from app.models.user import User
from app.schemas.author_schema import AuthorCreate, AuthorUpdate, AuthorSchema
from app.utils.jwt_guard import get_current_user
from app.utils.response_handler import response

router = APIRouter(prefix="/authors", tags=["authors"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Create a new author record for the current user.
    """
    # Check if author already exists for this user
    existing_author = db.query(Author).filter(
        Author.name == author_data.name, 
        Author.owner_id == current_user.id
    ).first()
    
    if existing_author:
        return response(
            success=False, 
            status_code=status.HTTP_400_BAD_REQUEST, 
            message="Author with this name already exists for you"
        )
    
    new_author = Author(
        name=author_data.name,
        bio=author_data.bio,
        owner_id=current_user.id
    )
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    
    return response(
        success=True, 
        status_code=status.HTTP_201_CREATED, 
        message="Author created successfully", 
        data=AuthorSchema.from_orm(new_author)
    )

@router.get("/")
async def get_authors(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10
):
    """
    List all authors owned by the current user with pagination.
    """
    authors = db.query(Author).filter(
        Author.owner_id == current_user.id
    ).order_by(Author.id.desc()).offset(page_size * (page - 1)).limit(page_size).all()
    
    total = db.query(Author).filter(
        Author.owner_id == current_user.id
    ).count()
    
    authors_data = [AuthorSchema.from_orm(author) for author in authors]
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Authors fetched successfully", 
        data=authors_data,
        meta={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }
    )

@router.get("/{author_id}")
async def get_author(
    author_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific author by ID.
    """
    author = db.query(Author).filter(
        Author.id == author_id, 
        Author.owner_id == current_user.id
    ).first()
    
    if not author:
        return response(
            success=False, 
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Author not found"
        )
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Author fetched successfully", 
        data=AuthorSchema.from_orm(author)
    )

@router.put("/{author_id}")
async def update_author(
    author_id: int, 
    author_data: AuthorUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing author's name or bio.
    """
    author = db.query(Author).filter(
        Author.id == author_id, 
        Author.owner_id == current_user.id
    ).first()
    
    if not author:
        return response(
            success=False, 
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Author not found"
        )
    
    if author_data.name is not None:
        author.name = author_data.name
    if author_data.bio is not None:
        author.bio = author_data.bio
        
    db.commit()
    db.refresh(author)
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Author updated successfully", 
        data=AuthorSchema.from_orm(author)
    )

@router.delete("/{author_id}")
async def delete_author(
    author_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Delete an author. Returns 409 Conflict if still referenced by books.
    """
    author = db.query(Author).filter(
        Author.id == author_id, 
        Author.owner_id == current_user.id
    ).first()
    
    if not author:
        return response(
            success=False, 
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Author not found"
        )
    
    # Check if author is referenced by any book
    referenced_book = db.query(Book).filter(Book.author_id == author_id).first()
    if referenced_book:
        return response(
            success=False,
            status_code=status.HTTP_409_CONFLICT,
            message="Cannot delete author: They are still referenced by one or more books."
        )
    
    db.delete(author)
    db.commit()
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Author deleted successfully"
    )
