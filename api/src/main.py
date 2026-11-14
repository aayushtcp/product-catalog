# Standard library imports
import os

# Third-party library imports
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from models import __all__  # Registers all SQLAlchemy models

# Project-specific imports
from product.router import router as product_router
from review.router import router as review_router
from category.router import router as category_router
from brand.router import router as brand_router
from collection.router import router as collection_router

# Global Imports
from constants import (
    ALLOWED_HTTP_METHODS,
    ALLOWED_REQUEST_HEADERS,
    APP_DESCRIPTION_KEY,
    APP_NAME_KEY,
    APP_VERSION_KEY,
    LIVE_WEB_APP_URL_KEY,
    LOCAL_WEB_APP_URL_KEY,
    MISSING_ENV_VARIABLE_PLACEHOLDER,
)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    version=os.getenv(APP_VERSION_KEY, MISSING_ENV_VARIABLE_PLACEHOLDER),
    title=os.getenv(APP_NAME_KEY, MISSING_ENV_VARIABLE_PLACEHOLDER),
    description=os.getenv(APP_DESCRIPTION_KEY, MISSING_ENV_VARIABLE_PLACEHOLDER),
)


# Configure CORS (Cross-Origin Resource Sharing) to allow specific origins
origins = [
    url
    for url in (
        os.getenv(LOCAL_WEB_APP_URL_KEY),
        os.getenv(LIVE_WEB_APP_URL_KEY),
    )
    if url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=ALLOWED_HTTP_METHODS,
    allow_headers=ALLOWED_REQUEST_HEADERS,
)

# Register routes
app.include_router(product_router)
app.include_router(review_router)
app.include_router(category_router)
app.include_router(brand_router)
app.include_router(collection_router)


# Redirect the root path ('/') to the Swagger UI documentation
@app.get("/", include_in_schema=False)
def show_docs():
    """
    Redirect users to the Swagger UI documentation.

    This route is excluded from the OpenAPI schema to avoid appearing in the documentation.
    """
    return RedirectResponse(url="/docs")
