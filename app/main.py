from fastapi import FastAPI
from app.utils.response_handler import response
from app.routes import user_routes, category_routes, author_routes, book_routes
from app.utils.jwt_guard import security
import app.models

app = FastAPI(title="Book Library API")

# Public routes (Login/Register)
app.include_router(user_routes.router)
app.include_router(category_routes.router)
app.include_router(author_routes.router)
app.include_router(book_routes.router)

@app.get("/")
def read_root():
    return response(success=True, status_code=200, message="Welcome to the Book Library API")
