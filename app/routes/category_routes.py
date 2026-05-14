from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.category import Category
from app.models.book import Book
from app.models.user import User
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategorySchema
from app.utils.jwt_guard import get_current_user
from app.utils.response_handler import response

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Create a new book category for the current user.
    """
    # Check if category already exists for this user
    existing_category = db.query(Category).filter(
        Category.name == category_data.name, 
        Category.owner_id == current_user.id
    ).first()
    
    if existing_category:
        return response(
            success=False, 
            status_code=status.HTTP_400_BAD_REQUEST, 
            message="Category with this name already exists for you"
        )
    
    new_category = Category(
        name=category_data.name,
        owner_id=current_user.id
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return response(
        success=True, 
        status_code=status.HTTP_201_CREATED, 
        message="Category created successfully", 
        data=CategorySchema.from_orm(new_category)
    )

@router.get("/")
async def get_categories(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10
):
    """
    List all categories owned by the current user with pagination.
    """
    categories = db.query(Category).filter(
        Category.owner_id == current_user.id
    ).order_by(Category.id.desc()).offset(page_size * (page - 1)).limit(page_size).all()
    
    total = db.query(Category).filter(
        Category.owner_id == current_user.id
    ).count()
    
    categories_data = [CategorySchema.from_orm(category) for category in categories]
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Categories fetched successfully", 
        data=categories_data,
        meta={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
        }
    )

@router.get("/{category_id}")
async def get_category(
    category_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific category by ID.
    """
    category = db.query(Category).filter(
        Category.id == category_id, 
        Category.owner_id == current_user.id
    ).first()
    
    if not category:
        return response(
            success=False, 
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Category not found"
        )
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Category fetched successfully", 
        data=CategorySchema.from_orm(category)
    )

@router.put("/{category_id}")
async def update_category(
    category_id: int, 
    category_data: CategoryUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing category name.
    """
    category = db.query(Category).filter(
        Category.id == category_id, 
        Category.owner_id == current_user.id
    ).first()
    
    if not category:
        return response(
            success=False, 
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Category not found"
        )
    
    if category_data.name:
        category.name = category_data.name
        
    db.commit()
    db.refresh(category)
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Category updated successfully", 
        data=CategorySchema.from_orm(category)
    )

@router.delete("/{category_id}")
async def delete_category(
    category_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Delete a category. Returns 409 Conflict if still referenced by books.
    """
    category = db.query(Category).filter(
        Category.id == category_id, 
        Category.owner_id == current_user.id
    ).first()
    
    if not category:
        return response(
            success=False, 
            status_code=status.HTTP_404_NOT_FOUND, 
            message="Category not found"
        )
    
    # Check if category is referenced by any book
    referenced_book = db.query(Book).filter(Book.category_id == category_id).first()
    if referenced_book:
        return response(
            success=False,
            status_code=status.HTTP_409_CONFLICT,
            message="Cannot delete category: It is still referenced by one or more books."
        )
    
    db.delete(category)
    db.commit()
    
    return response(
        success=True, 
        status_code=status.HTTP_200_OK, 
        message="Category deleted successfully"
    )
