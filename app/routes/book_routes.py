from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.database.database import get_db
from app.models.book import Book
from app.models.author import Author
from app.models.category import Category
from app.models.user import User
from app.schemas.book_schema import BookCreate, BookUpdate, BookSchema
from app.utils.jwt_guard import get_current_user
from app.utils.response_handler import response

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Add a new book to the library.
    Requires existing author and category belonging to the current user.
    """
    # Verify author exists and belongs to user
    author = db.query(Author).filter(Author.id == book_data.author_id, Author.owner_id == current_user.id).first()
    if not author:
        return response(success=False, status_code=404, message="Author not found or doesn't belong to you")

    # Verify category exists and belongs to user
    category = db.query(Category).filter(Category.id == book_data.category_id, Category.owner_id == current_user.id).first()
    if not category:
        return response(success=False, status_code=404, message="Category not found or doesn't belong to you")

    new_book = Book(
        **book_data.model_dump(),
        owner_id=current_user.id
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return response(
        success=True, 
        status_code=status.HTTP_201_CREATED, 
        message="Book created successfully", 
        data=BookSchema.from_orm(new_book)
    )

@router.get("/")
async def get_books(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    author_id: Optional[int] = None,
    category_id: Optional[int] = None,
    q: Optional[str] = None
):
    """
    Retrieve books owned by the current user.
    - **skip**: Pagination offset
    - **limit**: Max items to return
    - **author_id**: Filter by author
    - **category_id**: Filter by category
    - **q**: Search in title
    """
    query = db.query(Book).filter(Book.owner_id == current_user.id)
    
    # Filtering
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if category_id:
        query = query.filter(Book.category_id == category_id)
    
    # Search
    if q:
        query = query.filter(Book.title.ilike(f"%{q}%"))
    
    total = query.count()
    
    # Fetch with relationships to avoid N+1 queries
    books = query.options(
        joinedload(Book.author), 
        joinedload(Book.category)
    ).order_by(Book.id.desc()).offset(skip).limit(limit).all()
    
    books_data = [BookSchema.from_orm(book) for book in books]
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Books fetched successfully", 
        data=books_data,
        meta={
            "total": total,
            "skip": skip,
            "limit": limit,
            "page": (skip // limit) + 1
        }
    )

@router.get("/{book_id}")
async def get_book(
    book_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information for a specific book.
    """
    book = db.query(Book).options(
        joinedload(Book.author), 
        joinedload(Book.category)
    ).filter(Book.id == book_id, Book.owner_id == current_user.id).first()
    
    if not book:
        return response(success=False, status_code=404, message="Book not found")
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Book fetched successfully", 
        data=BookSchema.from_orm(book)
    )

@router.put("/{book_id}")
async def update_book(
    book_id: int, 
    book_data: BookUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Update details of an existing book.
    """
    book = db.query(Book).filter(Book.id == book_id, Book.owner_id == current_user.id).first()
    if not book:
        return response(success=False, status_code=404, message="Book not found")
    
    update_data = book_data.model_dump(exclude_unset=True)
    
    # Validate foreign keys if they are being updated
    if "author_id" in update_data:
        author = db.query(Author).filter(Author.id == update_data["author_id"], Author.owner_id == current_user.id).first()
        if not author:
             return response(success=False, status_code=404, message="Author not found or doesn't belong to you")
             
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"], Category.owner_id == current_user.id).first()
        if not category:
             return response(success=False, status_code=404, message="Category not found or doesn't belong to you")

    for key, value in update_data.items():
        setattr(book, key, value)
        
    db.commit()
    db.refresh(book)
    
    # Reload with relationships
    book = db.query(Book).options(joinedload(Book.author), joinedload(Book.category)).filter(Book.id == book_id).first()
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Book updated successfully", 
        data=BookSchema.from_orm(book)
    )

@router.delete("/{book_id}")
async def delete_book(
    book_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Remove a book from the library.
    """
    book = db.query(Book).filter(Book.id == book_id, Book.owner_id == current_user.id).first()
    if not book:
        return response(success=False, status_code=404, message="Book not found")
    
    db.delete(book)
    db.commit()
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Book deleted successfully"
    )
