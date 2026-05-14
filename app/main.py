from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.utils.response_handler import response
from slowapi.util import get_remote_address
from app.routes import user_routes, category_routes, author_routes, book_routes
import app.models
from app.utils.limiter import limiter

app = FastAPI(title="Book Library API")

# rate limiting configuration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Public routes (Login/Register)
app.include_router(user_routes.router)
app.include_router(category_routes.router)
app.include_router(author_routes.router)
app.include_router(book_routes.router)

@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    return response(success=True, status_code=200, message="Welcome to the Book Library API")
